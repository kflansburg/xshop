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
  Dir.glob("./#{prj}/*").each do |file|
    name = File.basename(file)
    if (name == 'test') # test dir
      lines['test'] = get_sloc_dir(file) 
    elsif (name == 'containers')
      lines['build'] = get_sloc_dir(file)
    elsif (name == 'config.yaml')
      lines['config'] = get_sloc(file)
    else
      get_sloc_dir(file)
    end
  end

  puts "Project : #{prj}"
  puts "\tTest : #{lines['test']}"
  puts "\tBuild : #{lines['build']}"
  puts "\tConfig : #{lines['config']}"
end
