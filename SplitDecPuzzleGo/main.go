package main

import (
	"bufio"
	"database/sql"
	"fmt"
	"log"
	"os"
	"sort"
	"time"

	"github.com/go-sql-driver/mysql"
)

var MIN_WORD_LENGTH int = 3
var MAX_WORD_LENGTH int = 12
var db *sql.DB
var debug bool = true

func main() {
	/* This program is designed to do a complete Split Decisions Puzzle
	 * generation workflow. I've broken this down into phases:
	 *   1. Find Split Decisions Word Pairs (SDWPs) from dictionary txts
	 *   2. Find constraints for SDWPs
	 *   3. Generate a board (or boards) using constrained SDWPs
	 */
	// Phase 1: Find SDWPs and store them in a SQL DB
	// set up sql DB
	dbUsername := ""
	dbPassword := ""
	dbUsername, dbPassword = parseSecretInfo("/Users/samtaylor/Documents/SQL_Secrets/sdwp_secrets.txt")
	setupDB(dbUsername, dbPassword)
	findSDWPs("/Users/samtaylor/Documents/SplitDecPuzzlePy/TextFiles/HandTrimmedUsableDictionary.txt", "/Users/samtaylor/Documents/SplitDecPuzzlePy/TextFiles/dictionary.txt")
	// check phase 1
	rows, err := db.Query("SELECT * FROM sdwps")
	if err != nil {
		print("error when checking phase 1!")
	}
	defer rows.Close()
	// Loop through rows, using Scan to assign column data to struct fields.
	count := 0
	for rows.Next() {
		count++
	}
	fmt.Printf("final table has %d rows\n", count)
}

func parseSecretInfo(secretsFile string) (dbUsername string, dbPassword string) {
	// parse secret info (SQL username and DB) from a txt file
	secretsList, err := os.Open(secretsFile)
	// catch error
	if err != nil {
		log.Fatal(err)
	}
	// remember to close the file at the end of the program
	defer secretsList.Close()
	// read the file into an array of words, using the scanner
	var secrets []string
	scanner := bufio.NewScanner(secretsList)
	for scanner.Scan() {
		secrets = append(secrets, scanner.Text())
	}
	// catch errors with scanner
	if err := scanner.Err(); err != nil {
		log.Fatal(err)
	}
	// parse secrets
	dbUsername = secrets[0]
	dbPassword = secrets[1]
	return dbUsername, dbPassword
}

func setupDB(username string, password string) {
	// DB is global so no need for params/returns
	cfg := mysql.Config{
		AllowNativePasswords: true,
		User:                 username,
		Passwd:               password,
		Net:                  "tcp",
		Addr:                 "127.0.0.1:3306",
		DBName:               "splitDecGen",
	}
	// get database handle
	var err error
	db, err = sql.Open("mysql", cfg.FormatDSN())
	if err != nil {
		log.Fatal(err)
	}
	pingErr := db.Ping()
	if pingErr != nil {
		log.Fatal(pingErr)
	}
	fmt.Println("successful DB connection! Woohoo!")
	db.Exec("DELETE FROM sdwps")
}

func findSDWPs(usableWordsFile string, referenceWordsFile string) {
	// Get SDWPs from words files
	// first get words arrays from the words files
	var start time.Time

	usableWords := getWordsArrayFromFile(usableWordsFile)
	referenceWords := getWordsArrayFromFile(referenceWordsFile)
	if debug {
		fmt.Println("Getting SDWPS from reference words")
		start = time.Now()
	}
	popDBFromWordsArray(referenceWords, false)
	if debug {
		elapsed := time.Since(start)
		fmt.Printf("  In total, took %s\n", elapsed)
	}
	if debug {
		fmt.Println("Getting SDWPs from usable words")
		start = time.Now()
	}
	popDBFromWordsArray(usableWords, true)
	if debug {
		elapsed := time.Since(start)
		fmt.Printf("  In total, took %s\n", elapsed)
	}
}

func popDBFromWordsArray(words [][]string, usable bool) {
	// Traverse all words. First by length, then alphabetically
	var start time.Time
	for l := MIN_WORD_LENGTH; l <= MAX_WORD_LENGTH; l++ {
		if debug {
			fmt.Printf("  Parsing %d-letter words... ", l)
			start = time.Now()
		}
		w := words[l-MIN_WORD_LENGTH]
		for rot := 0; rot < l-1; rot++ {
			for i := 0; i < len(w)-1; i++ {
				for j := i + 1; j < len(w); j++ {
					// if words don't have enough letters in common,
					// w[i] is out of viable matches. Move to next i.
					if w[i][:l-2] != w[j][:l-2] {
						break
					}
					// if words have exactly enough letters in common, this
					// is a match! Add to DB. w[i] might still have more
					// matches later though. Keep traversing.
					if w[i][l-1] != w[j][l-1] && w[i][l-2] != w[j][l-2] {
						// un-rotate words and add them to DB
						tmpWord1 := w[i][rot:] + w[i][:rot]
						tmpWord2 := w[j][rot:] + w[j][:rot]
						if usable {
							updateUsabilityDB(tmpWord1, tmpWord2)
						} else {
							uploadRefToDB(tmpWord1, tmpWord2, rot)
						}
					}
					// if words have too many letters in common, this isn't
					// a match, but w[i] might still have more matches later.
					// Keep traversing.
				}
				// once you completely move on from a word, rotate it by 1
				w[i] = w[i][l-1:] + w[i][:l-1]
			}
			// sort the list and repeat for the next rotation
			if rot < l-2 {
				sort.Strings(w)
			}
		}
		if debug {
			elapsed := time.Since(start)
			fmt.Printf("Took %s\n", elapsed)
		}
	}
}

func uploadRefToDB(word1 string, word2 string, rotation int) {
	//Start by getting trivial information.
	shapeLength := len(word1)
	mistakesId := 0
	usable := 0
	constraintsId := 0
	// interpret rotation to get shape_index, split_1, and split_2
	shapeIndex := shapeLength - 2 - rotation
	split1 := word1[shapeIndex : shapeIndex+2]
	split2 := word2[shapeIndex : shapeIndex+2]
	// set complex information (solution.
	// I used to also include prompt, but that's unnecessary.)
	var solution string
	for i := 0; i < len(word1); i++ {
		// for word1 == "sinew" and word2 == "screw"
		// solution would be: sew
		if i != shapeIndex && i != shapeIndex+1 {
			solution = solution + string(word1[i])
		}
	}
	// if the word wasn't entered before, then insert it into the db
	db.Exec("INSERT INTO sdwps (sdwp_id, word_1, word_2, split_1, split_2, shape_index, shape_length, solution, usable, mistakes_id, constraints_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 0, word1, word2, split1, split2, shapeIndex, shapeLength, solution, usable, mistakesId, constraintsId)
}

func updateUsabilityDB(word1 string, word2 string) {
	// if the word was entered before, then change its usable status to true and return
	db.Exec("SET usable=TRUE FROM sdwps WHERE word_1='%s' and word_2='%s'", word1, word2)
}

func getWordsArrayFromFile(filename string) [][]string {
	// Returns array of arrays of strings
	// Each internal array will be a list of words of the same length
	wordsInputList, err := os.Open(filename)
	// catch error
	if err != nil {
		log.Fatal(err)
	}
	// remember to close the file at the end of the program
	defer wordsInputList.Close()
	// read the file into an array of words, using the scanner
	var words []string
	scanner := bufio.NewScanner(wordsInputList)
	for scanner.Scan() {
		words = append(words, scanner.Text())
	}
	// set up the array of arrays
	var arrays [][]string
	for i := MIN_WORD_LENGTH; i <= MAX_WORD_LENGTH; i++ {
		var tmp []string
		arrays = append(arrays, tmp)
	}
	// go through the words array and filter into array of arrays
	for i := 0; i < len(words); i++ {
		index := len(words[i]) - MIN_WORD_LENGTH
		if MIN_WORD_LENGTH <= len(words[i]) && len(words[i]) <= MAX_WORD_LENGTH {
			arrays[index] = append(arrays[index], words[i])
		}
	}
	// sort the new array
	for i := 0; i < len(arrays); i++ {
		sort.Strings(arrays[i])
	}
	// catch errors with scanner
	if err := scanner.Err(); err != nil {
		log.Fatal(err)
	}
	return arrays
}
