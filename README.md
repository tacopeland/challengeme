# Challenge Me
This is a program meant to help me pick a programming project to do, what language to do it in, and any extra constraints to increase the difficulty.

## What will it do:
- It will randomly pick a challenge, language, and modifier for you, such as ["N Queens Problem", "Haskell", "Needs a really nice UI"] or ["BMI Calculator", "Rust", "Needs to be cross-platform"].
- If you accept a challenge, remove it from the possible challenges.
- Save stats about how many challenges I have done/am doing in which languages.
- Save stats about when you've finished challenges so it can pick "refactor x challenge" rather than a new challenge a month or two later.
- Pre-bundle some default challenges that will be imported into the main db (maybe sqlite?).
- Be able to insert and remove challenges from db.

## Challenge sources:
[x] Pro/g/ramming challenges v4.0 infograph.
[x] Project Euler.
[x] Protocols (get a list of RFCs, implement them).
[ ] Special.
  [ ] Find a trending Github repo in a certain language, get a pull request accepted.
  [ ] Pick some random algorithm from CLRS and implement it.
  [ ] Pick some random algorithm from An Introduction to Mathematical Cryptography and implement it.
[ ] Personally added challenges.

## Possible modifiers:
- Give it a really nice UI.
- Make it cross-platform and bundle it for Linux, Mac and Windows.
- Implement it as a modern, stylish website (make a backend API with CGI and stuff).
- Integrate its development with Jenkins.
- Do it on Windows.
- Do it on Mac.
- Do it on OpenBSD.
- Make it very parallel (use OpenCL if applicable).

## Challenge category object:
```py
category = {
	id: 1,
	name: "Project Euler",
	challenges: [],
	num-challenges: 700
}
```
The challenges attribute is the list of challenge objects, but if it's too much of a hassle to get the descriptions then we can just supply num-challenges while leaving challenges empty and we will only receive a challenge number when receiving the challenge.

## Possible challenge object:
```py
challenge = {
	id: 1,
	category: 1,
	description: "...",
	notes: "",
	languageConstraint: ["lang1", "lang2"],
	started: date,    # leave null if not started yet
	completed: date,  # leave null if not finished yet
	languageUsed: "lang2"
}
```

## Langs to start with:
- C
- C++
- Rust
- x86/64 Assembly
- MIPS Assembly
- ARM Assembly
- Python
- Haskell
- OCaml
- Common Lisp
- Scheme
- Clojure
- JavaScript
- Erlang
- Julia 
- COBOL

## Caveats:
- IMPORTANT: there cannot be commas in programming language names.
