package main

import (
	"encoding/json"
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
	return c.Render(http.StatusOK, "list", "This is First Page")
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

	file, err := os.Create("attendances.json")
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
