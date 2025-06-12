"""
Advanced algorithms for the Demon programming language.
"""

from typing import List, Dict, Any, Optional, Union, Callable, TypeVar, Generic
import heapq
import math

def register_advanced_algorithms(interpreter):
    """Register advanced algorithms with the interpreter."""
    NativeFunction = interpreter.NativeFunction
    
    # Dynamic Programming Algorithms
    
    # Fibonacci with memoization
    def fibonacci_memo(n):
        memo = {}
        
        def fib(n):
            if n in memo:
                return memo[n]
            if n <= 1:
                return n
            memo[n] = fib(n-1) + fib(n-2)
            return memo[n]
        
        return fib(n)
    
    # Longest Common Subsequence
    def lcs(str1, str2):
        m, n = len(str1), len(str2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if str1[i-1] == str2[j-1]:
                    dp[i][j] = dp[i-1][j-1] + 1
                else:
                    dp[i][j] = max(dp[i-1][j], dp[i][j-1])
        
        # Reconstruct the LCS
        i, j = m, n
        lcs_result = []
        
        while i > 0 and j > 0:
            if str1[i-1] == str2[j-1]:
                lcs_result.append(str1[i-1])
                i -= 1
                j -= 1
            elif dp[i-1][j] > dp[i][j-1]:
                i -= 1
            else:
                j -= 1
        
        return ''.join(reversed(lcs_result))
    
    # Knapsack problem
    def knapsack(weights, values, capacity):
        n = len(weights)
        dp = [[0] * (capacity + 1) for _ in range(n + 1)]
        
        for i in range(1, n + 1):
            for w in range(capacity + 1):
                if weights[i-1] <= w:
                    dp[i][w] = max(values[i-1] + dp[i-1][w-weights[i-1]], dp[i-1][w])
                else:
                    dp[i][w] = dp[i-1][w]
        
        # Reconstruct the solution
        w = capacity
        selected_items = []
        
        for i in range(n, 0, -1):
            if dp[i][w] != dp[i-1][w]:
                selected_items.append(i-1)
                w -= weights[i-1]
        
        return dp[n][capacity], selected_items
    
    # Edit Distance (Levenshtein)
    def edit_distance(str1, str2):
        m, n = len(str1), len(str2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if str1[i-1] == str2[j-1]:
                    dp[i][j] = dp[i-1][j-1]
                else:
                    dp[i][j] = 1 + min(dp[i-1][j],      # Delete
                                       dp[i][j-1],      # Insert
                                       dp[i-1][j-1])    # Replace
        
        return dp[m][n]
    
    # String Algorithms
    
    # Rabin-Karp string matching
    def rabin_karp(text, pattern):
        if not pattern:
            return [0]
        
        # Prime number for hash calculation
        q = 101
        d = 256  # Number of characters in the input alphabet
        
        m = len(pattern)
        n = len(text)
        
        if m > n:
            return []
        
        # Calculate hash value for pattern and first window of text
        p = 0  # hash value for pattern
        t = 0  # hash value for text
        h = 1
        
        # The value of h would be "pow(d, m-1) % q"
        for i in range(m-1):
            h = (h * d) % q
        
        # Calculate the hash value of pattern and first window of text
        for i in range(m):
            p = (d * p + ord(pattern[i])) % q
            t = (d * t + ord(text[i])) % q
        
        result = []
        
        # Slide the pattern over text one by one
        for i in range(n - m + 1):
            # Check the hash values of current window of text and pattern
            # If the hash values match then only check for characters one by one
            if p == t:
                # Check for characters one by one
                match = True
                for j in range(m):
                    if text[i + j] != pattern[j]:
                        match = False
                        break
                
                if match:
                    result.append(i)
            
            # Calculate hash value for next window of text
            if i < n - m:
                t = (d * (t - ord(text[i]) * h) + ord(text[i + m])) % q
                
                # We might get negative value of t, converting it to positive
                if t < 0:
                    t = t + q
        
        return result
    
    # Boyer-Moore string matching
    def boyer_moore(text, pattern):
        def build_bad_char_table(pattern):
            # Initialize all occurrences as -1
            bad_char = [-1] * 256
            
            # Fill the actual value of last occurrence of a character
            for i in range(len(pattern)):
                bad_char[ord(pattern[i])] = i
                
            return bad_char
        
        def build_good_suffix_table(pattern):
            m = len(pattern)
            suffix = [0] * m
            for i in range(m):
                j = 0
                while j < i and pattern[i-j] == pattern[m-j-1]:
                    j += 1
                suffix[i] = j
            
            return suffix
        
        m = len(pattern)
        n = len(text)
        
        if m > n:
            return []
        
        # Preprocessing
        bad_char = build_bad_char_table(pattern)
        
        # Search
        result = []
        s = 0  # s is shift of the pattern with respect to text
        
        while s <= n - m:
            j = m - 1
            
            # Keep reducing index j of pattern while characters of
            # pattern and text are matching at this shift s
            while j >= 0 and pattern[j] == text[s + j]:
                j -= 1
            
            # If the pattern is present at current shift, then j will become -1
            if j < 0:
                result.append(s)
                # Shift the pattern so that the next character in text
                # aligns with the last occurrence of it in pattern.
                s += (m - bad_char[ord(text[s + m])] if s + m < n else 1)
            else:
                # Shift the pattern so that the bad character in text
                # aligns with the last occurrence of it in pattern.
                s += max(1, j - bad_char[ord(text[s + j])])
        
        return result
    
    # Register functions with the interpreter
    interpreter.globals.define("fibonacci_memo", NativeFunction("fibonacci_memo", 1, fibonacci_memo))
    interpreter.globals.define("lcs", NativeFunction("lcs", 2, lcs))
    interpreter.globals.define("knapsack", NativeFunction("knapsack", 3, knapsack))
    interpreter.globals.define("edit_distance", NativeFunction("edit_distance", 2, edit_distance))
    interpreter.globals.define("rabin_karp", NativeFunction("rabin_karp", 2, rabin_karp))
    interpreter.globals.define("boyer_moore", NativeFunction("boyer_moore", 2, boyer_moore))