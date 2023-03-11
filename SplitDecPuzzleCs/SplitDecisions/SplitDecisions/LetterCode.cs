using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SplitDecisions
{
    internal static class LetterCode
    {
        private static readonly Dictionary<char, int> Encoder = Enumerable.Range(0, 26).ToDictionary(x => (char)((int)'a' + x), x => 1 << x);
        private static readonly Dictionary<int, char> Decoder = Enumerable.Range(0, 26).ToDictionary(x => 1 << x, x => (char)((int)'a' + x));

        public static int Encode(char letter)
        {
            return Encoder[letter];
        }

        public static List<char> Decode(int code)
        {
            List<char> letters = new() { };
            for (int i = 0; i < 26; i++)
            {
                if ((code | i) > 0)
                {
                    letters.Add(Decoder[i]);
                }
            }
            return letters;
        }
        /*
        public static int Convert(char letter)
        {
            return 1 << ((int)letter - (int)'a');
        }
        public static List<char> Convert(int code)
        {
            int bitmask;
            List<char> chars = new() { };
            for (int i = 0; i < 26; i++)
            {
                bitmask = 1 << i;
                if ((code | bitmask) == bitmask)
                {
                    chars.Add((char)((int)'a' + i));
                }
            }
            return chars;
        }*/
    }
}
