using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SplitDecisions
{
    internal static class LetterCode
    {

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
        }
    }
}
