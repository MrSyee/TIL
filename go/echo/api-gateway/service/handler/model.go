package handler

// API inputs, outputs
type sumRequest struct {
	InputX int `json:"inputX" form:"inputX" xml:"inputX"`
	InputY int `json:"inputY" form:"inputY" xml:"inputY"`
}

type sumResponse struct {
	Sum int `json:"sum" form:"sum" xml:"sum"`
}
