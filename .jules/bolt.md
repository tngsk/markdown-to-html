## 2024-05-10 - [O(M*N) String Replacement Bottleneck in Markdown Processor]
**Learning:** Sequential `str.replace` in a loop over dictionary items is highly inefficient for large text documents, especially when restoring many protected placeholders. It causes an O(M*N) bottleneck, where M is the number of placeholders and N is document length.
**Action:** Always use a single `re.sub` pass with a dictionary lookup function for bulk string replacements in text processing layers to reduce complexity to O(N).
