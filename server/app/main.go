package main

import (
	"encoding/json"
	"fmt"
	"html/template"
	"io"
	"net/http"
	"os"
	"time"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
)

type Template struct {
	templates *template.Template
}

type User struct {
	Id   int    `json:"id"`
	Name string `json:"name"`
}

type Attendance struct {
	Id        int       `json:"id"`
	Name      string    `json:"name"`
	TimeStart time.Time `json:"timeStart"`
	TimeGoal  time.Time `json:"timeGoal"`
	Users     []User    `json:"user"`
}

func (t *Template) Render(w io.Writer, name string, data interface{}, c echo.Context) error {
	return t.templates.ExecuteTemplate(w, name, data)
}

func main() {
	createDB()
	t := &Template{
		templates: template.Must(template.ParseGlob("views/*.html")),
	}
	// Echo instance
	e := echo.New()
	e.Renderer = t

	// Middleware
	e.Use(middleware.Logger())
	e.Use(middleware.Recover())

	// Routes
	e.GET("/", hello)
	e.GET("/list", list)

	// Start server
	e.Logger.Fatal(e.Start(":1323"))
}

// Handler
func hello(c echo.Context) error {
	return c.String(http.StatusOK, "Hello, World!")
}

func list(c echo.Context) error {
	// IDが指定されてくる
	x := 1
	attendances := loadAttendanceDB()
	fmt.Print("\n\n")
	fmt.Print(*loadAttendanceDB())
	fmt.Print("\n\n")
	for _, attendance := range *attendances {
		if attendance.Id == x {
			return c.Render(http.StatusOK, "list", attendance)
		}
	}
	return c.Render(http.StatusOK, "404.html", "This is First Page")
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
	return &attendances
}

func createDB() {
	attendances := []Attendance{
		{
			Id:        0,
			Name:      "点呼",
			TimeStart: time.Date(2024, 04, 29, 23, 8, 2, 0, &time.Location{}),
			TimeGoal:  time.Date(2024, 04, 29, 24, 8, 2, 0, &time.Location{}),
			Users:     []User{{1, "sotaro"}, {2, "sok"}},
		},
		{
			Id:        1,
			Name:      "コンピュータ部出席確認",
			TimeStart: time.Date(2024, 04, 30, 23, 8, 2, 0, &time.Location{}),
			TimeGoal:  time.Date(2024, 04, 30, 24, 8, 2, 0, &time.Location{}),
			Users:     []User{{1, "sotaro"}, {2, "sok"}},
		},
	}

	file, err := os.Create("./db/attendances.json")
	if err != nil {
		return
	}
	defer file.Close()

	encoder := json.NewEncoder(file)
	encoder.SetIndent("", "  ")
	if err := encoder.Encode(attendances); err != nil {
		return
	}
	return
}
