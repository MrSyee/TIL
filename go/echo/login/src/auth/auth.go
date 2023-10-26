package auth

import (
	"bufio"
	"encoding/csv"
	"os"

	"github.com/casbin/casbin/v2"
	"github.com/labstack/gommon/log"
	"gopkg.in/yaml.v3"

	db "echo-login/src/database"
)

// Configs
type Configs struct {
	AccessTokenExpire  int    `yaml:"AccessTokenExpire"`
	RefreshTokenExpire int    `yaml:"RefreshTokenExpire"`
	SecretKey          string `yaml:"SecretKey"`
	RefreshCookieName  string `yaml:"RefreshCookieName"`
	RedisServer        string `yaml:"RedisServer"`
}

var (
	enforcer   *casbin.Enforcer
	tokenCache *db.Cache
	Config     Configs
)

func init() {
	// Read secret configs.
	configFile, err := os.ReadFile("src/config/config.yaml")
	if err != nil {
		log.Fatal(err)
	}
	err = yaml.Unmarshal(configFile, &Config)
	if err != nil {
		log.Fatal(err)
	}

	// Load Casbin model and policy.
	enforcer, err = casbin.NewEnforcer(
		"src/config/authorization/model.conf",
		"src/config/authorization/policy.csv",
	)
	if err != nil {
		log.Fatal("error creating casbin model:", err)
	}

	// Define the token cache.
	tokenCache = db.NewCache(Config.RedisServer, Config.RefreshTokenExpire)

	// Get initial user info.
	file, err := os.Open("src/config/account.csv")
	if err != nil {
		log.Printf("error opening account info", err)
	}
	rdr := csv.NewReader(bufio.NewReader(file))
	rows, err := rdr.ReadAll()
	if err != nil {
		log.Fatal("error reading a csv file", err)
	}

	for _, row := range rows {
		role, name, pw := row[0], row[1], row[2]
		hashedPasswd, err := HashPassword(pw)
		if err != nil {
			log.Printf("failed to has the initial pw: ", err)
		}
		db.UserPasswordDB[name] = hashedPasswd
		db.UserRoleDB[name] = role
	}

	log.Printf("Token Cache: ", tokenCache)
	log.Printf("Enforcer: ", enforcer)
}
