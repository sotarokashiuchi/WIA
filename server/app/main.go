package main

import (
	"encoding/json"
	"fmt"
	"html/template"
	"io"
	"net/http"
	"os"
	"sort"
	"strconv"
	"time"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
	"golang.org/x/exp/slices"
)

type Template struct {
	templates *template.Template
}

type User struct {
	SerialNumber string    `json:"serialNumber"`
	Name         string    `json:"name"`
	TimeStanp    time.Time `json:"timeStanp"`
}

type Attendance struct {
	Id           int       `json:"id"`
	Name         string    `json:"name"`
	TimeStart    time.Time `json:"timeStart"`
	TimeGoal     time.Time `json:"timeGoal"`
	SerialNumber []string  `json:"serialNumber"`
}

func (t *Template) Render(w io.Writer, name string, data interface{}, c echo.Context) error {
	return t.templates.ExecuteTemplate(w, name, data)
}

func main() {
	fmt.Print("\n\n")
	createTestDB()
	t := &Template{
		templates: template.Must(template.ParseGlob("views/*/*.html")),
	}
	// Echo instance
	e := echo.New()
	e.Renderer = t

	// Middleware
	e.Use(middleware.Logger())
	e.Use(middleware.Recover())

	// Routes
	e.GET("/", hello)
	e.POST("/nfc/touch", nfcTouchPOST)
	e.GET("/user/edit", userEditGET)
	e.GET("/attendance/list", attendanceListGET)
	e.GET("/attendance/select", attendanceSelectGET)
	e.GET("/attendance/new", attendanceNewGET)
	e.POST("/attendance/new", attendanceNewPOST)

	// Start server
	e.Logger.Fatal(e.Start(":1234"))
}

// Handler
func hello(c echo.Context) error {
	return c.String(http.StatusOK, "Hello, World!")
}

func userEditGET(c echo.Context) error {
	users := loadUsersDB()
	return c.Render(http.StatusOK, "userEdit", *users)
}

func nfcTouchPOST(c echo.Context) error {
	/*
		// json形式ではなく、form形式で送信することにする
		POST /nfc/touch HTTP/1.1
		Host: localhost:1234
		Content-Type: application/x-www-form-urlencoded
		Content-Length: 14

		serialNumber=3
	*/

	serialNumber := c.FormValue("serialNumber")
	user := searchSerialNumber(serialNumber)
	attendances := loadAttendanceDB()

	if user.Name == "" {
		// usersDBに登録
		users := loadUsersDB()
		if user.SerialNumber == "" {
			*users = append(*users, User{
				SerialNumber: serialNumber,
				TimeStanp:    time.Now(),
			})
		} else {
			for i, user := range *users {
				if user.SerialNumber == serialNumber {
					(*users)[i].TimeStanp = time.Now()
				}
			}
		}
		createDB("./db/users.json", *users)
	}

	// 受付中の出席管理があれば出席にする
	for i, attendance := range *attendances {
		if time.Now().After(attendance.TimeStart) && time.Now().Before(attendance.TimeGoal) {
			// 受付中
			for _, serialNum := range attendance.SerialNumber {
				if serialNum == serialNumber {
					return c.JSON(http.StatusOK, user)
				}
			}
			(*attendances)[i].SerialNumber = append(attendance.SerialNumber, serialNumber)
			createDB("./db/attendances.json", *attendances)
		}
	}

	return c.JSON(http.StatusOK, user)
}

func attendanceNewGET(c echo.Context) error {
	attendances := loadAttendanceDB()
	var attendanceNameList []string

	for _, attendance := range *attendances {
		attendanceNameList = append(attendanceNameList, attendance.Name)
	}

	sort.Slice(attendanceNameList, func(i, j int) bool {
		return attendanceNameList[i] < attendanceNameList[j]
	})

	return c.Render(http.StatusOK, "attendanceNew", slices.Compact(attendanceNameList))
}

func attendanceNewPOST(c echo.Context) error {
	// ToDo: 出席管理実施時刻が被っていないか検証
	dateStart, _ := time.Parse("2006-01-02T15:04:05Z07:00", c.FormValue("dateStart")+"T"+c.FormValue("timeStart")+":00+"+"00:00")
	dateGoal, _ := time.Parse("2006-01-02T15:04:05Z07:00", c.FormValue("dateGoal")+"T"+c.FormValue("timeGoal")+":00+"+"00:00")
	id := insertDB(
		Attendance{
			Name:      c.FormValue("name"),
			TimeStart: dateStart,
			TimeGoal:  dateGoal,
		},
	)
	return c.Render(http.StatusOK, "attendanceCompleted", id)
}

func attendanceSelectGET(c echo.Context) error {
	attendances := loadAttendanceDB()
	return c.Render(http.StatusOK, "attendanceSelect", *attendances)
}

func attendanceListGET(c echo.Context) error {
	id, err := strconv.Atoi(c.QueryParam(("id")))
	if err != nil {
		return c.Render(http.StatusOK, "404.html", "Cant't to Found Page")
	}

	attendances := loadAttendanceDB()
	for _, attendance := range *attendances {
		if attendance.Id == id {
			return c.Render(http.StatusOK, "attendanceList", attendance)
		}
	}
	return c.Render(http.StatusOK, "404.html", "This is First Page")
}

func searchSerialNumber(serialNumber string) User {
	users := loadUsersDB()
	for _, user := range *users {
		if user.SerialNumber == serialNumber {
			return user
		}
	}
	return User{}
}

func loadUsersDB() *[]User {
	file, err := os.Open("./db/users.json")
	if err != nil {
		return nil
	}
	defer file.Close()

	var users []User
	decoder := json.NewDecoder(file)
	if err := decoder.Decode(&users); err != nil {
		return nil
	}

	sort.Slice(users, func(i, j int) bool {
		return users[i].TimeStanp.After(users[j].TimeStanp)
	})

	return &users
}

func loadAttendanceDB() *[]Attendance {
	file, err := os.Open("./db/attendances.json")
	if err != nil {
		return nil
	}
	defer file.Close()

	var attendances []Attendance
	decoder := json.NewDecoder(file)
	if err := decoder.Decode(&attendances); err != nil {
		return nil
	}

	sort.Slice(attendances, func(i, j int) bool {
		return attendances[i].Id > attendances[j].Id
	})

	return &attendances
}

func insertDB(attendance Attendance) int {
	attendances := loadAttendanceDB()
	attendance.Id = (*attendances)[0].Id + 1
	*attendances = append(*attendances, attendance)

	createDB("./db/attendances.json", *attendances)
	return attendance.Id
}

func createTestDB() {
	var users interface{}
	users = []User{
		{
			SerialNumber: "0",
			Name:         "kashi",
		},
		{
			SerialNumber: "1",
			Name:         "sotaro",
		},
		{
			SerialNumber: "2",
			Name:         "sok",
		},
	}
	createDB("./db/users.json", users)

	var attendances interface{}
	attendances = []Attendance{
		{
			Id:           0,
			Name:         "点呼",
			TimeStart:    time.Date(2024, 04, 29, 23, 8, 2, 0, &time.Location{}),
			TimeGoal:     time.Date(2024, 04, 29, 24, 8, 2, 0, &time.Location{}),
			SerialNumber: []string{"1", "0"},
		},
		{
			Id:           1,
			Name:         "コンピュータ部出席確認",
			TimeStart:    time.Date(2024, 04, 30, 23, 8, 2, 0, &time.Location{}),
			TimeGoal:     time.Date(2024, 04, 30, 24, 8, 2, 0, &time.Location{}),
			SerialNumber: []string{"1", "2"},
		},
		{
			Id:           2,
			Name:         "点呼",
			TimeStart:    time.Date(2024, 05, 01, 0, 0, 0, 0, &time.Location{}),
			TimeGoal:     time.Date(2024, 05, 05, 23, 8, 2, 0, &time.Location{}),
			SerialNumber: []string{"1", "2"},
		},
	}
	createDB("./db/attendances.json", attendances)
	return
}

func createDB(DBName string, data interface{}) {
	file, err := os.Create(DBName)
	if err != nil {
		return
	}
	defer file.Close()

	encoder := json.NewEncoder(file)
	encoder.SetIndent("", "  ")
	if err := encoder.Encode(data); err != nil {
		return
	}
}
