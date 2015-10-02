require 'fileutils'

projects = ['GHOST',
            'Shellshock', 
            'CVE-2013-6629', # libjpeg
            'CVE-2010-4221-Metasploit',
            'Heartbleed']

def read_specials(file)
  num = File.readlines(file).count do |line| 
    line.strip
    line != '' &&  !line.start_with?('#')
  end
  return num
end

def whitelist?(file)
  whitelist = ['Dockerfile', 'config.yaml', 'docker-compose.yml']
  whitelist.include? File.basename(file)
end

def get_sloc_dir(dir)
  num = 0
  Dir.glob("#{dir}/**/*").each do |file|
    num += get_sloc(file)
  end
  num
end

def get_sloc(file)
  num = 0
  if (whitelist?(file)) 
    num = read_specials(file)
  else
    num = _get_sloc(file)
  end
  #puts "#{file} : #{num}"
  return num
end

def _get_sloc(file)
  output = `sloccount #{file}`
  output[/\(SLOC\)\s+= (\d+)/]
  num = $1.to_i
  return num
end

def calc_sloc(dir)
  Dir["#{dir}/**/*"]
end

projects.each do |prj|
  lines = {:test => 0, :build => 0} 
  lines['test'] = get_sloc("#{prj}/test/xshop_test.py")
  lines['build'] = get_sloc_dir("#{prj}/containers")
  lines['config'] = get_sloc("#{prj}/config.yaml")

  puts "Project : #{prj}"
  puts "\tConfig : #{lines['config']}"
  puts "\tBuild : #{lines['build']}"
  puts "\tTest : #{lines['test']}"
end