package main

import (
	"fmt"
	"math"
	"math/rand"
	"runtime"
	"strings"
)

func hello() {
	fmt.Println("Hello, 世界, 세계")
}

func randInt() {
	fmt.Println("My favorite number is ", rand.Intn(10))
}

func mathSqrt() {
	fmt.Println("Now you have $g problems\n", math.Sqrt(7))
}

func add(x, y int) int {
	return x + y
}

func swap(x, y string) (string, string) {
	return y, x
}

func split(sum int) (x, y int) {
	x = sum * 4 / 9
	y = sum - x
	return
}

func variablesBoolean() (bool, bool, string, int, int) {
	var c, python, java = true, false, "true!"
	var i int = 10
	k := 5
	return c, python, java, i, k
}

func convertType() (int, int, float64, uint) {
	x, y := 3, 4
	var f float64 = math.Sqrt(float64(x*x + y*y))
	var z uint = uint(f)
	return x, y, f, z
}

func forLoop() {
	sum := 0
	for i := 0; i < 10; i++ {
		sum += i
	}
	fmt.Println(sum)

	sum2 := 1
	for sum2 < 1000 {
		sum2 += sum2
	}
	fmt.Println(sum2)
}

func ifCondition(x float64) {
	if x < 0 {
		fmt.Println(fmt.Sprint(math.Sqrt(-x)) + "i")
	} else {
		fmt.Println(math.Sqrt(x))
	}
}

func Sqrt(x float64) float64 {
	z := 1.0
	for math.Round(z*z*1e5)/1e5 != x {
		z -= (z*z - x) / (2 * z)
	}
	return z
}

func SwitchOs() {
	fmt.Print("Go runs on ")
	switch os := runtime.GOOS; os {
	case "darwin":
		fmt.Println("OS X.")
	case "linux":
		fmt.Println("Linux.")
	default:
		fmt.Printf("%s. \n", os)
	}
}

func ExampleDefer() {
	fmt.Println("counting")
	defer fmt.Println("Reverse order like stack")
	for i := 0; i < 10; i++ {
		defer fmt.Println(i)
	}

	fmt.Println("done")
}

func ExampleDefer2() {
	i := 0
	defer fmt.Println(i)
	i++
	return
}

func Array() {
	var a [2]string
	a[0] = "Hello"
	a[1] = "World"
	fmt.Println(a[0], a[1])
	fmt.Println(a)

	primes := [6]int{2, 3, 5, 7, 11, 13}
	fmt.Println(primes)
}

func ArraySlice() {
	names := [4]string{
		"John",
		"Paul",
		"George",
		"Ringo",
	}
	fmt.Println(names)

	a := names[0:2]
	b := names[1:3]
	fmt.Println(a, b)

	b[0] = "XXX"
	fmt.Println(a, b)
	fmt.Println(names)
}

func Array2D(dx, dy int) [][]uint8 {
	picture := make([][]uint8, dy)
	for i := range picture {
		picture[i] = make([]uint8, dx)
	}

	for x := 0; x < dx; x++ {
		for y := 0; y < dy; y++ {
			picture[y][x] = uint8(y)
		}
	}
	return picture
}

type Vertex struct {
	Lat, Long float64
}

func Map() map[string]Vertex {
	m := make(map[string]Vertex)
	m["Bell Labs"] = Vertex{
		40.68433, -74.39967,
	}
	return m
}

func WordCount(s string) map[string]int {
	wordCount := make(map[string]int)
	for _, val := range strings.Fields(s) {
		wordCount[val] += 1
	}
	return wordCount
}

func adder() func(int) int {
	sum := 0
	return func(x int) int {
		sum += x
		return sum
	}
}

func fibonacciCloser() func() int {
	prev := 0
	curr := 1
	tmp := 0

	return func() int {
		tmp = prev + curr
		prev = curr
		curr = tmp
		return curr
	}
}

// method: Receiver
type Vertex2 struct {
	X, Y float64
}

func (v *Vertex2) Scale(f float64) {
	v.X = v.X * f
	v.Y = v.Y * f
}
func (v Vertex2) Abs() float64 {
	return math.Sqrt(v.X*v.X + v.Y*v.Y)
}

func main() {
	hello()
	randInt()
	mathSqrt()

	fmt.Println(add(3, 4))
	fmt.Println(swap("hello", "world"))
	fmt.Println(split(17))
	fmt.Println(variablesBoolean())
	fmt.Println(convertType())

	forLoop()

	ifCondition(2)
	ifCondition(-2)

	fmt.Println(Sqrt(3))

	SwitchOs()
	ExampleDefer()
	ExampleDefer2()

	Array()
	ArraySlice()

	fmt.Println(Array2D(6, 6))
	m := Map()
	fmt.Println(m)
	fmt.Println(m["Bell Labs"])
	v, ok := m["Bell Labs"]
	fmt.Println("The value:", v, "Present?", ok)

	fmt.Println(WordCount("I learn Go language!"))

	pos, neg := adder(), adder()
	for i := 0; i < 10; i++ {
		fmt.Println(
			pos(i),
			neg(-2*i),
		)
	}

	f := fibonacciCloser()
	for i := 0; i < 10; i++ {
		fmt.Println(f())
	}

	v2 := Vertex2{3, 4}
	fmt.Println(v2.Abs())
	v2.Scale(10)
	fmt.Println(v2.Abs())
}
