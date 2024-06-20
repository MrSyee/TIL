package database

// Fake DB: User -> Password Hash
// Fake DB: User -> Role
var UserPasswordDB map[string]string = map[string]string{}
var UserRoleDB map[string]string = map[string]string{}
