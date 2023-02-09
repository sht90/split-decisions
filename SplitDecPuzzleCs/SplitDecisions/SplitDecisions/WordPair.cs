﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SplitDecisions
{
    internal class WordPair : IComparable, IComparable<WordPair>
    {
        public Shape Shape;
        public string[] Words;
        public string[] Splits;
        public string Letters;
        public string Before;
        public string After;
        public int Usability;
        public List<int> Mistakeables;
        public List<int> Anchors;

        public WordPair(Shape shape, string word1, string word2, int usability)
        {
            this.Shape = shape;
            this.Words = new string[] { word1, word2 };
            this.Splits = new string[] {
                word1[shape.Index..(shape.Index+2)],
                word2[shape.Index..(shape.Index+2)]
            };
            this.Before = word1[..shape.Index];
            this.After = word1[(shape.Index + 2)..];
            this.Letters = Before + After;
            this.Mistakeables = new List<int> { };
            this.Anchors = new List<int> { };
            this.Usability = usability;
        }

        public override string ToString()
        {
            return String.Format("{0}({1}/{2}){3}", Before, Splits[0], Splits[1], After);
        }

        public string GetPrompt()
        {
            string tmpBefore = String.Concat("-", Before.Length);
            string tmpAfter = String.Concat("-", After.Length);
            return String.Format("{0}({1}/{2}){3}", tmpBefore, Splits[0], Splits[1], tmpAfter);
        }

        public int CompareTo(object? other)
        {
            if (other == null)
            {
                return 1;
            }
            if (other is WordPair wordPair)
            {
                return this.CompareTo(wordPair);
            }
            throw new ArgumentException("Object is not a WordPair");
        }

        public int CompareTo(WordPair? other)
        {
            if (other == null)
            {
                return 1;
            }
            // Compare WordPairs by shape
            int compareByShape = this.Shape.CompareTo(other.Shape);
            if (compareByShape != 0)
            {
                return compareByShape;
            }
            // Compare WordPairs by prompt
            int compareByPrompt;
            for (int i = 0; i < this.Splits.Length; i++)
            {
                compareByPrompt = this.Splits[i].CompareTo(other.Splits[i]);
                if (compareByPrompt != 0)
                {
                    return compareByPrompt;
                }
            }
            // Compare WordPairs by solution
            return this.Letters.CompareTo(other.Letters);
        }
    }
}
