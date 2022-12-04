package client

// Request input type
type sumRequest struct {
	InputX int `json:"inputX"`
	InputY int `json:"inputY"`
}

// Request output type
type sumResponse struct {
	Sum int `json:"sum"`
}
