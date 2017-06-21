# Anagram Solver - Dennis Sauve
# Usage: Command Line - ruby anagrammer.rb [word] [-d --duplicate]

def check(word, text, duplicate)
  if word.length < text.length
    return false
  elsif duplicate
    return word.uniq.sort == text.uniq.sort
  else
    return word.sort == text.sort
  end
end

def main
  text = ARGV[0].split('')
  ARGV.include?('-d') || ARGV.include?('--duplicate') ? duplicate = true : duplicate = false
  words = File.open('enable1.txt').read.split("\r\n")
  possibilities = []
  words.each do |word|
    if check(word.split(''), text, duplicate)
      possibilities << word
    end
  end
  puts possibilities
end

main()