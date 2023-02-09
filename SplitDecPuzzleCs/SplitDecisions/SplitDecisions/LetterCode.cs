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
            return 1 << (letter % 32);
        }
        public static char Convert(int code)
        {
            for (char c = 'a'; c <= 'z', c++)
            {

            }
        }
    }
}
