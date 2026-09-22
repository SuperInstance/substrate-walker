using System;

namespace SubstrateWalker
{
    public class Program
    {
        const ulong FNV_OFFSET = 0xcbf29ce484222325UL;
        const ulong FNV_PRIME = 0x100000001b3UL;
        
        public static ulong Fnv1a64(string input)
        {
            ulong h = FNV_OFFSET;
            byte[] bytes = System.Text.Encoding.UTF8.GetBytes(input);
            foreach (byte b in bytes)
            {
                h ^= b;
                h *= FNV_PRIME;
            }
            return h;
        }
        
        public static void Main()
        {
            Console.WriteLine("=== Substrate Walker C# Port — FNV-1a 64-bit ===");
            Console.WriteLine();
            
            var reference = new (string input, ulong expected)[]
            {
                ("", 0xcbf29ce484222325UL),
                ("a", 0xaf63dc4c8601ec8cUL),
                ("foobar", 0x85944171f73967e8UL),
                ("abc", 0xe71fa2190541574bUL),
                ("café Δ 日本語", 0x024a555471370b18dUL),
                ("witness log is the prediction", 0x176137b542efe82aUL),
            };
            
            bool allPass = true;
            foreach (var (input, expected) in reference)
            {
                ulong got = Fnv1a64(input);
                string status = (got == expected) ? "✓" : "✗";
                if (got != expected) allPass = false;
                Console.WriteLine($"{status} '{input}': 0x{got:x16} (expected 0x{expected:x16})");
            }
            Console.WriteLine();
            Console.WriteLine(allPass 
                ? "All 6 reference vectors match — fleet canary pinned ✓"
                : "MISMATCH — investigate!");
            Environment.Exit(allPass ? 0 : 1);
        }
    }
}
