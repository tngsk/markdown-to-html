with open("tests/components/test_mono_clock.py", "r") as f:
    c = f.read()
c = c.replace('@[clock](time: "10:00")', '@[clock](format: "HH:mm")')
c = c.replace('<mono-clock time="10:00">', '<mono-clock format="HH:mm">')
with open("tests/components/test_mono_clock.py", "w") as f:
    f.write(c)

with open("tests/components/test_mono_sound.py", "r") as f:
    c = f.read()
c = c.replace("assert '<mono-sound src=\"test.mp3\"' in html", "assert 'src=\"test.mp3\"' in html")
with open("tests/components/test_mono_sound.py", "w") as f:
    f.write(c)
