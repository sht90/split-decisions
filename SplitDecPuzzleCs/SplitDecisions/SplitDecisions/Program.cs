﻿// See https://aka.ms/new-console-template for more information
using SplitDecisions;

Console.WriteLine("Hello World");

// Set some readonlys. These should probably be inputs/arguments/configs in the future.
// board dimensions
int BOARD_LENGTH = 13;
int BOARD_WIDTH = 13;
// other board settings
int MINIMUM_USABILITY = (int)Usability.BOTH_WORDS;
int MINIMUM_WORD_LENGTH = 3;
int MAXIMUM_WORD_LENGTH = 10;
BoardSettings settings = new(MINIMUM_USABILITY, BOARD_WIDTH, BOARD_LENGTH, MINIMUM_WORD_LENGTH, MAXIMUM_WORD_LENGTH);
// dictionaries (in the literal sense, not like the Dictionary<A,B> sense)
string USABLE_DICTIONARY_PATH = "/Users/samtaylor/Documents/GitHub/split-decisions/SplitDecPuzzleCs/TextFiles/UsableDictionary.txt";
string REFERENCE_DICTIONARY_PATH = "/Users/samtaylor/Documents/GitHub/split-decisions/SplitDecPuzzleCs/TextFiles/ReferenceDictionary.txt";

WordPairsFinder wordPairsFinder = new(settings);
List<WordPair> wordPairs = wordPairsFinder.FindWordPairs(USABLE_DICTIONARY_PATH, REFERENCE_DICTIONARY_PATH);
Console.WriteLine(wordPairs.Count.ToString());
//foreach(WordPair wordPair in wordPairs) { Console.WriteLine(wordPair.ToString()); }