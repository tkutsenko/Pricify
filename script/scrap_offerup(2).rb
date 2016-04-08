#!/usr/bin/env ruby

require 'rest_client'
require 'trollop'
require 'pry'

opts = Trollop::options do
  opt :cookie_file, "File with working cookie", :type => :string
  opt :save_to, "Dir where to save results", :type => :string
  opt :start_index, "Starting index to scrap", :type => :integer
  opt :num_to_scrap, "How many pages to scrap", :type => :integer
  opt :pause, "Seconds to sleep between requests", :type => :string
  opt :prefix, "Prefix for saved files", :type => :string
end
Trollop::die "All options but prefix must be present" if opts.select { |k, v| k != :prefix }.values.any?(&:nil?)

save_dir = opts[:save_to]
cookie = File.read(opts[:cookie_file])
start_index = opts[:start_index]
num_to_scrap = opts[:num_to_scrap]
prefix = opts[:prefix]
pause = opts[:pause].to_f

headers = {
  'X-Requested-With' => 'XMLHttpRequest',
  'Referer' => 'https://offerupnow.com/',
  'Connection' => 'keep-alive',
  'User-Agent' => 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36',
  'Cookie' => cookie
}

num_to_scrap.times do |i|
  page = start_index + i
  begin
    response = RestClient.get "https://offerupnow.com/?type=recent-list&page=#{page}", headers
    File.write("#{save_dir}/#{prefix}%0.4d.json" % page, response.body)
    puts "Scraped page #{page}"
    STDOUT.flush
    sleep pause
  rescue => e
    puts "Error scraping page #{page}: #{e.message}"
    STDOUT.flush
  end
end
