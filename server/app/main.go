package main

import (
	"encoding/csv"
	"encoding/json"
	"fmt"
	"html/template"
	"io"
	"log"
	"math/rand"
	"net/http"
	"os"
	"os/exec"
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

type SimpleTime struct {
	Year   int `json:"year"`
	Month  int `json:"month"`
	Day    int `json:"day"`
	Hour   int `json:"hour"`
	Minut  int `json:"minut"`
	Second int `json:"second"`
}

type User struct {
	SerialNumber string     `json:"serialNumber"`
	Name         string     `json:"name"`
	TimeStanp    SimpleTime `json:"timeStanp"`
}

type Attendance struct {
	Id           int        `json:"id"`
	Name         string     `json:"name"`
	Status       string     `json:"status"` // nil , running or stopping
	TimeStart    SimpleTime `json:"timeStart"`
	TimeGoal     SimpleTime `json:"timeGoal"`
	SerialNumber []string   `json:"serialNumber"`
}

var jst *time.Location

func transToSimpleTimeFromTime(time time.Time) SimpleTime {
	return transToSimpleTimeFromInt(
		time.Year(),
		int(time.Month()),
		time.Day(),
		time.Hour(),
		time.Minute(),
		time.Second(),
	)
}

func transToTimeFromSimpleTime(simpleTime SimpleTime) time.Time {
	return time.Date(
		simpleTime.Year,
		time.Month(simpleTime.Month),
		simpleTime.Day,
		simpleTime.Hour,
		simpleTime.Minut,
		simpleTime.Second,
		0,
		jst,
	)
}

func transToSimpleTimeFromInt(year, month, day, hour, minut, second int) SimpleTime {
	return SimpleTime{
		Year:   year,
		Month:  month,
		Day:    day,
		Hour:   hour,
		Minut:  minut,
		Second: second,
	}
}

func (t *Template) Render(w io.Writer, name string, data interface{}, c echo.Context) error {
	return t.templates.ExecuteTemplate(w, name, data)
}

func main() {
	jst, _ = time.LoadLocation("Asia/Tokyo")
	fmt.Print("\n\n")
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
	e.Static("/static", "static")
	e.GET("/", index)
	e.GET("/reset", reset)
	e.GET("/sample", sample)
	e.POST("/nfc/touch", nfcTouchPOST)
	e.GET("/user/edit", userEditGET)
	e.POST("/user/edit", userEditPOST)
	e.GET("/attendance/list", attendanceListGET)
	e.GET("/attendance/download", attendanceDownloadGET)
	e.GET("/attendance/select", attendanceSelectGET)
	e.GET("/attendance/status", attendanceStatusGET)
	e.GET("/attendance/new", attendanceNewGET)
	e.POST("/attendance/new", attendanceNewPOST)
	e.GET("/setting/", settingIndexGET)
	e.POST("/setting/nfcTouch", settingNfcTouchPOST)
	e.GET("/setting/time", settingTimeGET)
	e.POST("/setting/adduser", settingAdduserPOST)

	// Start server
	e.Logger.Fatal(e.Start(":1234"))
}

// Handler
func reset(c echo.Context) error {
	attendanceFile, err := os.Create("./db/attendances.json")
	if err != nil {
		return c.String(http.StatusInternalServerError, "Server Error")
	}
	defer attendanceFile.Close()
	attendanceFile.WriteString("[{}]")

	userFile, err := os.Create("./db/users.json")
	if err != nil {
		return c.String(http.StatusInternalServerError, "Server Error")
	}
	defer userFile.Close()
	userFile.WriteString("[]")

	return c.Redirect(http.StatusFound, "/")
}

func sample(c echo.Context) error {
	createTestDB()
	return c.Redirect(http.StatusFound, "/")
}

func index(c echo.Context) error {
	return c.Render(http.StatusOK, "index", "")
}

func attendanceDownloadGET(c echo.Context) error {
	id, err := strconv.Atoi(c.QueryParam(("id")))
	if err != nil {
		return c.Render(http.StatusOK, "404.html", "Cant't to Found Page")
	}

	attendances := loadAttendanceDB()
	var fileName string
	for _, attendance := range *attendances {
		if attendance.Id == id {
			var csv [][]string
			csv = append(csv, []string{"ID:" + strconv.Itoa(attendance.Id), "Name:" + attendance.Name})
			csv = append(csv, []string{"出席者", "出席時刻"})

			for _, serialNumber := range attendance.SerialNumber {
				user := searchSerialNumber(serialNumber)
				csv = append(csv, []string{user.Name, transToTimeFromSimpleTime(user.TimeStanp).String()})
			}

			fileName = strconv.Itoa(id) + ".csv"
			createCSV("./tmp/"+fileName, csv)
		}
	}
	return c.Attachment("./tmp/"+fileName, fileName)
}

func userEditPOST(c echo.Context) error {
	users := loadUsersDB()
	for i, user := range *users {
		(*users)[i].Name = c.FormValue("name-" + user.SerialNumber)
	}
	createDB("./db/users.json", *users)
	return c.Render(http.StatusOK, "userEdit", *users)
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
	user := nfcTouch(serialNumber)
	return c.JSON(http.StatusOK, user)
}

func nfcTouch(serialNumber string) User {
	user := searchSerialNumber(serialNumber)
	attendances := loadAttendanceDB()

	// usersDBに登録
	users := loadUsersDB()
	if user.SerialNumber == "" {
		*users = append(*users, User{
			SerialNumber: serialNumber,
			TimeStanp:    transToSimpleTimeFromTime(time.Now().In(jst)),
		})
	} else {
		for i, user := range *users {
			if user.SerialNumber == serialNumber {
				(*users)[i].TimeStanp = transToSimpleTimeFromTime(time.Now().In(jst))
			}
		}
	}
	createDB("./db/users.json", *users)

	// 受付中の出席管理があれば出席にする
	for i, attendance := range *attendances {
		if attendance.Status == "running" {
			for _, serialNum := range attendance.SerialNumber {
				if serialNum == serialNumber {
					return user
				}
			}
			(*attendances)[i].SerialNumber = append(attendance.SerialNumber, serialNumber)
			createDB("./db/attendances.json", *attendances)
			return user
		}
	}

	// 受付中の出席管理が存在しないので、今日の日付の出席管理を作成する
	nowTime := time.Now()
	today := (strconv.Itoa(nowTime.Year()) +"/"+ strconv.Itoa(int(nowTime.Month())) +"/"+ strconv.Itoa(nowTime.Day()))

	for _, attendance := range *attendances {
		if attendance.Name == today {
			return user
		}
	}

	setAttendance := Attendance{
		Name:      today,
		Status:    "running",
		TimeStart: transToSimpleTimeFromTime(time.Date(nowTime.Year(), nowTime.Month(), nowTime.Day(), 0, 0, 0, 0, nowTime.Location())), // locationの設定が必要かも
		TimeGoal:  transToSimpleTimeFromTime(time.Date(nowTime.Year(), nowTime.Month(), nowTime.Day(), 23, 59, 99, 99, nowTime.Location())),
		SerialNumber: []string{serialNumber},
	}

	insertDB(setAttendance)

	return user
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
	attendances := loadAttendanceDB()
	dateStart, _ := time.Parse("2006-01-02T15:04:05Z07:00", c.FormValue("dateStart")+"T"+c.FormValue("timeStart")+":00+"+"09:00")
	dateGoal, _ := time.Parse("2006-01-02T15:04:05Z07:00", c.FormValue("dateGoal")+"T"+c.FormValue("timeGoal")+":00+"+"09:00")
	setAttendance := Attendance{}
	if c.FormValue("submit") == "running" {
		// runningの出席簿があればstoppingする
		for i, attendance := range *attendances {
			if attendance.Status == "running" {
				(*attendances)[i].Status = "stopping"
			}
		}
		setAttendance = Attendance{
			Name:   c.FormValue("name"),
			Status: "running",
		}
	}
	if c.FormValue("submit") == "nil" {
		setAttendance = Attendance{
			Name:      c.FormValue("name"),
			Status:    "nil",
			TimeStart: transToSimpleTimeFromTime(dateStart),
			TimeGoal:  transToSimpleTimeFromTime(dateGoal),
		}
		if time.Now().In(jst).After(dateStart) && time.Now().In(jst).Before(dateGoal) {
			setAttendance.Status = "running"
			for i, attendance := range *attendances {
				if attendance.Status == "running" {
					fmt.Println("stoppingss")
					(*attendances)[i].Status = "stopping"
				}
			}
		}
	}
	createDB("./db/attendances.json", *attendances)
	id := insertDB(setAttendance)
	return c.Render(http.StatusOK, "attendanceCompleted", id)
}

func settingIndexGET(c echo.Context) error {
	users := loadUsersDB()
	return c.Render(http.StatusOK, "settingIndex", *users)
}

func settingNfcTouchPOST(c echo.Context) error {
	serialNumber := c.FormValue("SerialNumber")
	nfcTouch(serialNumber)
	return c.Redirect(http.StatusFound, "/setting/")
}

func settingTimeGET(c echo.Context) error {
	setTime, _ := time.Parse("2006-01-02T15:04:05.999Z", c.QueryParam(("time")))
	setTime = setTime.In(jst)

	dateArg := fmt.Sprintf("%d/%02d/%02d %02d:%02d",
		setTime.Year(),
		setTime.Month(),
		setTime.Day(),
		setTime.Hour(),
		setTime.Minute(),
	)

	cmd := exec.Command("sudo", "date", "-s", dateArg)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr

	err := cmd.Run()
	if err != nil {
		log.Fatal(err)
	}

	return c.String(http.StatusOK, "OK")
}

func settingAdduserPOST(c echo.Context) error {
	rng := rand.New(rand.NewSource(time.Now().UnixNano()))
	UserName := c.FormValue("UserName")
	var serialNumber string

	users := loadUsersDB()
	for {
		serialNumber = fmt.Sprintf("[%d, %d, %d, %d, %d]", rng.Intn(255), rng.Intn(255), rng.Intn(255), rng.Intn(255), rng.Intn(255))
		for _, user := range *users {
			if user.SerialNumber == serialNumber {
				continue
			}
		}
		break
	}

	*users = append(*users, User{
		SerialNumber: serialNumber,
		Name: UserName,
		TimeStanp:    transToSimpleTimeFromTime(time.Now().In(jst)),
	})
	createDB("./db/users.json", *users)

	return c.Redirect(http.StatusFound, "/setting/")
}

func attendanceSelectGET(c echo.Context) error {
	attendances := loadAttendanceDB()
	return c.Render(http.StatusOK, "attendanceSelect", *attendances)
}

func attendanceStatusGET(c echo.Context) error {
	id, _ := strconv.Atoi(c.QueryParam(("id")))
	attendances := loadAttendanceDB()

	for i, attendance := range *attendances {
		if attendance.Id == id {
			(*attendances)[i].Status = c.QueryParam(("status"))
		} else {
			if attendance.Status == "running" {
				(*attendances)[i].Status = "stopping"
			}
		}
	}

	createDB("./db/attendances.json", *attendances)

	return c.String(http.StatusOK, "OK")
}

func attendanceListGET(c echo.Context) error {
	type htmlAttendance struct {
		Attendance Attendance
		Users      []User
	}

	id, err := strconv.Atoi(c.QueryParam(("id")))
	if err != nil {
		return c.Render(http.StatusOK, "404.html", "Cant't to Found Page")
	}

	attendances := loadAttendanceDB()
	for _, attendance := range *attendances {
		if attendance.Id == id {
			var users []User

			for _, serialNumber := range attendance.SerialNumber {
				user := searchSerialNumber(serialNumber)
				users = append(users, user)
			}

			return c.Render(http.StatusOK, "attendanceList", htmlAttendance{Attendance: attendance, Users: users})
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
		return transToTimeFromSimpleTime(users[i].TimeStanp).After(transToTimeFromSimpleTime(users[j].TimeStanp))
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

	for i, attendance := range attendances {
		if !(time.Now().In(jst).After(transToTimeFromSimpleTime(attendance.TimeStart)) && time.Now().In(jst).Before(transToTimeFromSimpleTime(attendance.TimeGoal))) {
			if attendance.Status == "running" && attendance.TimeStart.Year != 0 {
				fmt.Println("stopping")
				fmt.Println(transToTimeFromSimpleTime(attendance.TimeStart).Year())
				attendances[i].Status = "stopping"
			}
		}
	}
	createDB("./db/attendances.json", attendances)

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
			TimeStanp:    transToSimpleTimeFromTime(time.Now().In(jst)),
		},
		{
			SerialNumber: "1",
			Name:         "sotaro",
			TimeStanp:    transToSimpleTimeFromTime(time.Now().In(jst)),
		},
		{
			SerialNumber: "2",
			Name:         "souchan",
			TimeStanp:    transToSimpleTimeFromTime(time.Now().In(jst)),
		},
	}
	createDB("./db/users.json", users)

	var attendances interface{}
	attendances = []Attendance{
		{
			Id:           0,
			Name:         "点呼",
			Status:       "nil",
			TimeStart:    transToSimpleTimeFromTime(time.Date(2024, 04, 29, 23, 8, 2, 0, jst)),
			TimeGoal:     transToSimpleTimeFromTime(time.Date(2024, 04, 29, 24, 8, 2, 0, jst)),
			SerialNumber: []string{"1", "0"},
		},
		{
			Id:           1,
			Name:         "コンピュータ部出席確認",
			Status:       "nil",
			TimeStart:    transToSimpleTimeFromTime(time.Date(2024, 04, 30, 23, 8, 2, 0, jst)),
			TimeGoal:     transToSimpleTimeFromTime(time.Date(2024, 04, 30, 24, 8, 2, 0, jst)),
			SerialNumber: []string{"1", "2"},
		},
		{
			Id:           2,
			Name:         "点呼",
			Status:       "running",
			TimeStart:    transToSimpleTimeFromTime(time.Date(2024, 05, 01, 0, 0, 0, 0, jst)),
			TimeGoal:     transToSimpleTimeFromTime(time.Date(2024, 05, 05, 23, 8, 2, 0, jst)),
			SerialNumber: []string{"1", "2"},
		},
	}
	createDB("./db/attendances.json", attendances)
	return
}

func createCSV(fileName string, data [][]string) {
	fmt.Print("\n\n", data)
	file, err := os.Create(fileName)
	if err != nil {
		fmt.Print(err)
		return
	}
	defer file.Close()

	writer := csv.NewWriter(file)
	defer writer.Flush()
	for _, line := range data {
		writer.Write(line)
	}
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
