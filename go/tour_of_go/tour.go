package main

import (
	"fmt"
	"math"
	"math/rand"
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

func main() {
	hello()
	randInt()
	mathSqrt()

	fmt.Println(add(3, 4))
	fmt.Println(swap("hello", "world"))
	fmt.Println(split(17))
	fmt.Println(variablesBoolean())
	fmt.Println(convertType())
}
