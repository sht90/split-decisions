package main

import (
	"bufio"
	"database/sql"
	"fmt"
	"log"
	"os"
	"sort"
	"strings"
	"time"

	"github.com/go-sql-driver/mysql"
)

var MIN_WORD_LENGTH int = 3
var MAX_WORD_LENGTH int = 12
var db *sql.DB
var debug bool = true
var phase1Complete bool = false

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
	if !phase1Complete {
		db.Exec("DELETE FROM sdwps")
		findSDWPs("/Users/samtaylor/Documents/SplitDecPuzzlePy/TextFiles/HandTrimmedUsableDictionary.txt", "/Users/samtaylor/Documents/SplitDecPuzzlePy/TextFiles/dictionary.txt")
		var start time.Time
		if debug {
			fmt.Println("Performing bulk update from CSV files...")
			start = time.Now()
		}
		bulkAddCSVsToDB()
		if debug {
			elapsed := time.Since(start)
			fmt.Printf("  In total, took %s\n", elapsed)
		}
		// verify findSDWPs
		rows, err := db.Query("SELECT * FROM sdwps")
		if err != nil {
			print("error when checking phase 1!")
		}
		defer rows.Close()
		count := 0
		for rows.Next() {
			count++
		}
		fmt.Printf("final table has %d rows\n", count)
		// verify usable SDWPs too
		rows, err = db.Query("SELECT * FROM sdwps WHERE usable = 1")
		if err != nil {
			print("error when checking phase 1!")
		}
		defer rows.Close()
		count = 0
		for rows.Next() {
			count++
		}
		fmt.Printf("final table has %d usable sdwps\n", count)
	}
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
		DBName:               "splitDecGen2",
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
}

func findSDWPs(usableWordsFile string, referenceWordsFile string) {
	// Get SDWPs from words files
	// first get words arrays from the words files
	var start time.Time

	usableWords := getWordsArrayFromFile(usableWordsFile)
	referenceWords := getWordsArrayFromFile(referenceWordsFile)
	if debug {
		fmt.Println("Getting SDWPS...")
		start = time.Now()
	}
	popCSVFromWordsArray(usableWords, referenceWords, "referenceSDWPS.csv")
	if debug {
		elapsed := time.Since(start)
		fmt.Printf("  In total, took %s\n", elapsed)
	}
}

func popCSVFromWordsArray(usableWords [][]string, words [][]string, outputCSV string) {
	// Traverse all words. First by length, then alphabetically
	var start time.Time
	var outCSVLines []string
	for l := MIN_WORD_LENGTH; l <= MAX_WORD_LENGTH; l++ {
		if debug {
			fmt.Printf("  Parsing %d-letter words... ", l)
			start = time.Now()
		}
		w := words[l-MIN_WORD_LENGTH]
		uw := usableWords[l-MIN_WORD_LENGTH]
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
						tmpWord1Index := sort.SearchStrings(uw, tmpWord1)
						tmpWord2Index := sort.SearchStrings(uw, tmpWord2)
						tmpUsable := tmpWord1Index >= 0 && tmpWord1Index < len(uw) && tmpWord2Index >= 0 && tmpWord2Index < len(uw) && uw[tmpWord1Index] == tmpWord1 && uw[tmpWord2Index] == tmpWord2
						outCSVLines = append(outCSVLines, stringSdwp(tmpWord1, tmpWord2, rot, tmpUsable))
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
	stringArrToCSV(outCSVLines, outputCSV)
}

func stringSdwp(word1 string, word2 string, rotation int, usableBool bool) string {
	// build string
	retString := ""
	// and now just start appending values...
	retString += word1 + "," + word2 + ","
	// Get trivial information.
	shapeLength := len(word1)
	mistakesId := 0
	usable := 0
	if usableBool {
		usable = 1
	}
	constraintsId := 0
	// interpret rotation to get shape_index, split_1, and split_2
	shapeIndex := shapeLength - 2 - rotation
	split1 := word1[shapeIndex : shapeIndex+2]
	split2 := word2[shapeIndex : shapeIndex+2]
	retString += split1 + "," + split2 + ","
	retString += fmt.Sprint(shapeIndex) + "," + fmt.Sprint(shapeLength) + ","
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
	retString += solution + ","
	retString += fmt.Sprint(usable) + "," + fmt.Sprint(mistakesId) + "," + fmt.Sprint(constraintsId)
	return retString
}

func stringArrToCSV(arr []string, outFile string) {
	f, err := os.OpenFile(outFile, os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		fmt.Println(err)
		return
	}
	defer f.Close()
	for i := 0; i < len(arr); i++ {
		_, err = fmt.Fprintln(f, arr[i])
		if err != nil {
			fmt.Println(err)
		}
	}
}

func bulkAddCSVsToDB() {
	mysql.RegisterLocalFile("referenceSDWPS.csv")
	_, err := db.Exec("LOAD DATA LOCAL INFILE 'referenceSDWPS.csv' INTO TABLE sdwps FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' (word_1, word_2, split_1, split_2, shape_index, shape_length, solution, usable, mistakes_id, constraints_id)")
	if err != nil {
		fmt.Println("db.ExecContext", err)
		return
	}
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
		words = append(words, strings.ToUpper(scanner.Text()))
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
