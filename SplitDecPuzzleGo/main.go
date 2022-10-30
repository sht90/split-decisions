package main

import (
	"bufio"
	"log"
	"os"
	"sort"
)

var MIN_WORD_LENGTH int = 3
var MAX_WORD_LENGTH int = 12

func main() {
	/* This program is designed to do a complete Split Decisions Generation
	 * workflow. I've broken this down into phases:
	 *   1. Find Split Decisions Word Pairs (SDWPs) from dictionary txts
	 *   2. Find constraints for SDWPs
	 *   3. Generate a board (or boards) using constrained SDWPs
	 */

}

func findSDWPs(usableWordsFile string, referenceWordsFile string) {
	// Get SDWPs from words files
	// first get words arrays from the words files
	usableWords := getWordsArrayFromFile(usableWordsFile)
	referenceWords := getWordsArrayFromFile(referenceWordsFile)
	popDBFromWordsArray(usableWords)
	popDBFromWordsArray(referenceWords)
}

func popDBFromWordsArray(words [][]string) {
	// Traverse all words. First by length, then alphabetically
	for l := MIN_WORD_LENGTH; l <= MAX_WORD_LENGTH; l++ {
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
						uploadToDB(tmpWord1, tmpWord2)
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
	}
}

func uploadToDB(word1 string, word2 string) {

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
