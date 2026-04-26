with open('src/components/mono-poll/style.css', 'r') as f:
    content = f.read()

# Add height: 100% and flex to :host
# This is what I did originally which makes the poll stretch IF the parent allows it.
# The user wants "pollのみでいいです" which means "only for poll".
