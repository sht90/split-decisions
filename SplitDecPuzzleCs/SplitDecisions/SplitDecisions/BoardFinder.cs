using System;
namespace SplitDecisions
{
    internal class BoardFinder
    {

        enum Entropy
        {
            Resolved,
            //ForcedEmpty, // don't make a ForcedEmpty entropy, just make the cell empty when you place the WordPair
            Anchor,
            Floater,
            Default
        }

        private int MinWordLength;
        private int MaxWordLength;
        private int Height;
        private int Width;
        private List<WordPair> WordPairs = new() { };
        Entropy[][] boardEntropy;
        string[][] board;
        int[]? tb;
        int[]? tw;
        List<WordPair> usedWordPairs;
        List<string> usedPrompts;
        List<string> usedWords;

        public BoardFinder(BoardSettings settings)
        {
            // Parse settings
            MinWordLength = settings.MinWordLength;
            MaxWordLength = settings.MaxWordLength;
            Height = settings.BoardHeight;
            Width = settings.BoardWidth;
            // Make initial board, including entropy
            boardEntropy = Enumerable.Repeat(Enumerable.Repeat(Entropy.Default, Width).ToArray(), Height).ToArray();
            board = Enumerable.Repeat(Enumerable.Repeat("", Width).ToArray(), Height).ToArray();
            // Make the lists for keeping track of which wordPairs/words/prompts we've used so far. We don't want any repeats.
            // Normally you'd just remove these things from the list, but since the list of Wordpairs (10k-100k) is so huge compared to the list of used WordPairs on the board (10-100), it's probably computationally cheaper just to check whether a word has been used yet.
            usedWordPairs = new() { };
            usedPrompts = new() { };
            usedWords = new() { };
        }

        public void ResetBoard()
        {
            // reset board for everything except which words/prompts/wordPairs have been used already.
            boardEntropy = Enumerable.Repeat(Enumerable.Repeat(Entropy.Default, Width).ToArray(), Height).ToArray();
            board = Enumerable.Repeat(Enumerable.Repeat("", Width).ToArray(), Height).ToArray();
            tb = null;
            tw = null;
        }

        // Find one board. Even if we could make every single board during my lifetime, most of them would be duplicates except for one 3-letter WordPair. Parsing the results would be harder than just generating a new one from scratch with a different seed. 
        public List<List<string>> FindBoard(List<WordPair> wordPairs, int seed = -1)
        {
            // setup
            // get traversal order for board (just top half) and word pairs list
            // abbreviate these because I'll be using them a lot, but Traversal Order Board -> tb and Traversal Order WordPairs -> tw.
            tb = Enumerable.Range(0, (int)Math.Ceiling(Height * 0.5) * Width).ToArray();
            tw = Enumerable.Range(0, wordPairs.Count).ToArray();
            // shuffle traversal order
            Random rng = (seed < 0) ? new() : new(seed);
            FisherYatesShuffle(rng, tb);
            FisherYatesShuffle(rng, tw);
            
            // return the results of the recursive solving algorithm
            return Solve();
        }

        public List<List<string>> Solve()
        {
            return null;
        }

        public bool Reject()
        {
            return false;
        }

        public bool IsFullSolution()
        {
            return false;
        }

        public void Extend()
        {
            return;
        }

        public void Next()
        {
            return;
        }

        private static void FisherYatesShuffle<T>(Random rng, T[] array)
        {
            // basically, for each index in the array, swap it with a random index.
            int n = array.Length;
            while (n > 1)
            {
                int k = rng.Next(n--);
                T temp = array[n];
                array[n] = array[k];
                array[k] = temp;
            }
            // this is O(n), which is the fastest reputable shuffling alg I could find.
        }
    }
}

