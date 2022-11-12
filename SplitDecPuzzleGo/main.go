package main

import (
	"bufio"
	"fmt"
	"log"
	"os"
	"sort"
	"strings"
	"time"
)

var MIN_WORD_LENGTH int = 3
var MAX_WORD_LENGTH int = 12
var debug bool = true
var sdwps []SDWP
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

type Shape struct {
	length, index int
}

type FastPrompt struct {
	shapeId int
	splitX1 int
	splitX2 int
}

type SDWP struct {
	// Each split decisions word pair (SDWP) is defined by the following strings:
	// the two words that comprise the split decisions (ex. sinew, screw),
	// the two strings used in the split portion of the SDWP (ex. in, cr),
	// the two strings used in the joint portions of the SDWP (ex. s, ew).
	word1, word2, split1, split2, joint1, joint2 string
	// The SDWP also has metadata to make common operations quicker:
	// the shape says what space an SDWP would occupy on the board (ex. -|--)
	shape Shape
	// the prompt is all the info the user sees from a blank puzzle (ex. -(i/c|n/r)--)
	prompt FastPrompt
	// if the sdwp is usable in a board
	usable bool
}

// populate all the struct fields of an sdwp just from word1, word2, rotation
func SdwpConstructor(word1 string, word2 string, rot int) SDWP {
	// get shape
	_shape := Shape{
		length: len(word1),
		index:  len(word1) - 2 - rot,
	}
	// get shapeId for fast prompt
	n := _shape.length - MIN_WORD_LENGTH + 1
	sumn := n * (n + 1) / 2
	_shapeId := sumn - 1 + _shape.index
	// get splitX1 and splitX2 for fast prompt
	_splitX1 := letter2BitString[word1[_shape.index]] | letter2BitString[word2[_shape.index]]
	_splitX2 := letter2BitString[word1[_shape.index+1]] | letter2BitString[word2[_shape.index+1]]
	_prompt := FastPrompt{
		shapeId: _shapeId,
		splitX1: _splitX1,
		splitX2: _splitX2,
	}
	// actually make the struct now
	return SDWP{
		word1:  word1,
		word2:  word2,
		split1: word1[_shape.index : _shape.index+2],
		split2: word2[_shape.index : _shape.index+2],
		joint1: word1[:_shape.index],
		joint2: word1[_shape.index+2:],
		shape:  _shape,
		prompt: _prompt,
		usable: false,
	}
}

func main() {
	/* This program is designed to do a complete Split Decisions Puzzle
	 * generation workflow. I've broken this down into phases:
	 *   1. Find Split Decisions Word Pairs (SDWPs) from dictionary txts
	 *   2. Find constraints for SDWPs
	 *   3. Generate a board (or boards) using constrained SDWPs
	 */
	// Phase 1: Find SDWPs and store them in an array
	findSDWPs("/Users/samtaylor/Documents/SplitDecPuzzlePy/TextFiles/HandTrimmedUsableDictionary.txt", "/Users/samtaylor/Documents/SplitDecPuzzlePy/TextFiles/dictionary.txt")
}

func compareShapes(shape1 Shape, shape2 Shape) int {
	if shape1.length > shape2.length {
		return 1
	} else if shape2.length > shape1.length {
		return -1
	} else if shape1.index > shape2.index {
		return 1
	} else if shape2.index > shape1.index {
		return -1
	}
	return 0
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

						} else {
							// put the sdwp in the array. It's guaranteed to be in sorted order
							sdwps = append(sdwps, SdwpConstructor(tmpWord1, tmpWord2, rot))
							// update metadata arrays
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
