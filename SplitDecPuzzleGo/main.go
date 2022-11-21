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

var letter2BitString = map[byte]int{
	'a': 0b10000000000000000000000000,
	'b': 0b01000000000000000000000000,
	'c': 0b00100000000000000000000000,
	'd': 0b00010000000000000000000000,
	'e': 0b00001000000000000000000000,
	'f': 0b00000100000000000000000000,
	'g': 0b00000010000000000000000000,
	'h': 0b00000001000000000000000000,
	'i': 0b00000000100000000000000000,
	'j': 0b00000000010000000000000000,
	'k': 0b00000000001000000000000000,
	'l': 0b00000000000100000000000000,
	'm': 0b00000000000010000000000000,
	'n': 0b00000000000001000000000000,
	'o': 0b00000000000000100000000000,
	'p': 0b00000000000000010000000000,
	'q': 0b00000000000000001000000000,
	'r': 0b00000000000000000100000000,
	's': 0b00000000000000000010000000,
	't': 0b00000000000000000001000000,
	'u': 0b00000000000000000000100000,
	'v': 0b00000000000000000000010000,
	'w': 0b00000000000000000000001000,
	'x': 0b00000000000000000000000100,
	'y': 0b00000000000000000000000010,
	'z': 0b00000000000000000000000001,
}
var bitString2Letter = map[int]string{
	0b10000000000000000000000000: "a",
	0b01000000000000000000000000: "b",
	0b00100000000000000000000000: "c",
	0b00010000000000000000000000: "d",
	0b00001000000000000000000000: "e",
	0b00000100000000000000000000: "f",
	0b00000010000000000000000000: "g",
	0b00000001000000000000000000: "h",
	0b00000000100000000000000000: "i",
	0b00000000010000000000000000: "j",
	0b00000000001000000000000000: "k",
	0b00000000000100000000000000: "l",
	0b00000000000010000000000000: "m",
	0b00000000000001000000000000: "n",
	0b00000000000000100000000000: "o",
	0b00000000000000010000000000: "p",
	0b00000000000000001000000000: "q",
	0b00000000000000000100000000: "r",
	0b00000000000000000010000000: "s",
	0b00000000000000000001000000: "t",
	0b00000000000000000000100000: "u",
	0b00000000000000000000010000: "v",
	0b00000000000000000000001000: "w",
	0b00000000000000000000000100: "x",
	0b00000000000000000000000010: "y",
	0b00000000000000000000000001: "z",
}

var MIN_WORD_LENGTH int = 3
var MAX_WORD_LENGTH int = 12
var db *sql.DB
var debug bool = true
var phase1Complete bool = true
var phase2Complete bool = false

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
	// Phase 2: find metadata and add to the DB
	if !phase2Complete {
		getConstraints("mistakeables.csv", "constraints.csv")
	}
}

func getConstraints(mistakeablesFile string, constraintsFile string) {
	// first, get an array of sdwps sorted by prompt
	solns, ids := getSdwpSolutionsByPrompt()
	fmt.Printf("len(solns) = %d\nlen(solns[0]) = %d)", len(solns), len(solns[0]))
	os.Exit(0)
	// also, set up our output arrays
	var mistakeablesCSV []string
	var constraintsCSV []string
	// traverse prompts
	for p, prompt := range solns {
		if p%1000 == 0 {
			fmt.Printf("analyzing prompt %d", p)
		}
		// traverse solutions of sdwps with the same prompt
		for s, currentSoln := range prompt {
			currentId := ids[p][s]
			// get initial array of mistakeables and constraints
			var mistakeables []int
			var constraints [][]int
			for i := 0; i < len(currentSoln); i++ {
				mistakeables = append(mistakeables, 0)
			}
			// traverse other solutions with the same prompt
			for o, otherSoln := range prompt {
				if o != s {
					// for each letter that could be mistaken for another letter,
					// mark that in the mistakeables array.
					for i := range mistakeables {
						if currentSoln[i] != otherSoln[i] {
							mistakeables[i] |= letter2BitString[otherSoln[i]]
						}
					}
				}
			}
			// congrats! You've found all the mistakeables. Add them to the CSV string array
			outputString := fmt.Sprintf("%d,", currentId)
			for i := 0; i < MAX_WORD_LENGTH; i++ {
				if i < len(mistakeables) {
					outputString += fmt.Sprintf("%d", mistakeables[i])
				}
				if i < MAX_WORD_LENGTH-1 {
					outputString += ","
				}
			}
			mistakeablesCSV = append(mistakeablesCSV, outputString)
			// now, to find constraints.
			if len(prompt) == 1 {
				cc := make([]int, len(mistakeables))
				constraints = append(constraints, cc)
			} else {
				var letterIndeces []int
				for index := range currentSoln {
					letterIndeces = append(letterIndeces, index)
				}
				for size := range letterIndeces {
					combos := combinations(size, letterIndeces)
					for _, combo := range combos {
						constrainsAll := true
						for o, otherSoln := range prompt {
							if o != s {
								for _, l := range combo {
									if currentSoln[l] != otherSoln[l] {
										constrainsAll = false
										break
									}
								}
								if constrainsAll {
									// 0 by default
									cc := make([]int, len(mistakeables))
									for _, l := range combo {
										cc[l] = 1
									}
									constraints = append(constraints, cc)
									// you've found constraints! Now add them to the CSV
									conOutString := fmt.Sprintf("%d,", currentId)
									for i := 0; i < MAX_WORD_LENGTH; i++ {
										if i < len(cc) {
											conOutString += fmt.Sprintf("%d", cc[i])
										}
										if i < MAX_WORD_LENGTH-1 {
											conOutString += ","
										}
									}
									constraintsCSV = append(constraintsCSV, conOutString)
								}
							}
						}
					}
				}
			}
		}
	}
	print("finished getting metadata")
	stringArrToCSV(mistakeablesCSV, mistakeablesFile)
	stringArrToCSV(constraintsCSV, constraintsFile)
}

func combinations(size int, inputArray []int) [][]int {
	return combinationsHelper(size, []int{}, inputArray, [][]int{})
}

func combinationsHelper(size int, solved []int, unsolved []int, output [][]int) [][]int {
	// base case: if solved is of the right size, add it to the output
	if len(solved) == size {
		// or rather, add a copy, not the solved thing itself
		solvedCopy := make([]int, len(solved))
		copy(solvedCopy, solved)
		output = append(output, solvedCopy)
		return output
	}
	// recursive call: traverse the list to find new value to add to solved portion
	for i, r := range unsolved {
		solved = append(solved, r)
		unsolvedCopy := make([]int, len(unsolved))
		copy(unsolvedCopy, unsolved)
		output = combinationsHelper(size, solved, unsolvedCopy[i+1:], output)
		solved = solved[:len(solved)-1]
	}
	return output
}

func getSdwpSolutionsByPrompt() ([][]string, [][]int) {
	// start with some setup:
	var (
		sdwpSolutions [][]string
		sdwpIds       [][]int
		prevLeng      int    = -1
		prevIndx      int    = -1
		prevSpl1      string = ""
		prevSpl2      string = ""
	)
	// now do the actual database query. Here we want to find the solution for each sdwp,
	// sorted by prompt. Prompt is comprised of shape and splits.
	// We also need to query for the prompt itself, since we'll compare successive prompts
	// so that everything with the same prompt is grouped together.
	rows, err := db.Query("SELECT sdwp_id, solution, shape_length, shape_index, split_1, split_2 FROM sdwps ORDER BY shape_length, shape_index, split_1, split_2")
	if err != nil {
		fmt.Printf("Error %v", err)
	}
	// alright, we made it this far. So we have all the data we need
	defer rows.Close()
	// traverse all the rows, one by one
	for rows.Next() {
		// each row has these contents:
		var (
			id   int
			soln string
			leng int
			indx int
			spl1 string
			spl2 string
		)
		if err := rows.Scan(&id, &soln, &leng, &indx, &spl1, &spl2); err != nil {
			log.Fatal(err)
		}
		// if any of these contents aren't the same as their previous contents,
		if (leng != prevLeng) || (indx != prevIndx) || (spl1 != prevSpl1) || (spl2 != prevSpl2) {
			// overwrite the previous contents and append a new nested array
			prevLeng = leng
			prevIndx = indx
			prevSpl1 = spl1
			prevSpl2 = spl2
			sdwpSolutions = append(sdwpSolutions, []string{soln})
			sdwpIds = append(sdwpIds, []int{id})
		} else {
			// if the prompt is the same, add the solution to the previously established nested array
			sdwpSolutions[len(sdwpSolutions)-1] = append(sdwpSolutions[len(sdwpSolutions)-1], soln)
			sdwpIds[len(sdwpIds)-1] = append(sdwpIds[len(sdwpIds)-1], id)
		}
	}
	fmt.Println("Finished getting sdwpSolutions and sdwpIds")
	return sdwpSolutions, sdwpIds
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
						// un-rotate words and see if they appear in the usable dictionary
						tmpWord1 := w[i][rot:] + w[i][:rot]
						tmpWord2 := w[j][rot:] + w[j][:rot]
						tmpWord1Index := sort.SearchStrings(uw, tmpWord1)
						tmpWord2Index := sort.SearchStrings(uw, tmpWord2)
						tmpUsable := tmpWord1Index >= 0 && tmpWord1Index < len(uw) && tmpWord2Index >= 0 && tmpWord2Index < len(uw) && uw[tmpWord1Index] == tmpWord1 && uw[tmpWord2Index] == tmpWord2
						// add new sdwp to CSV lines array
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
	// convert array of csv lines to an actual csv file, which can be bulk-inserted into DB
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
