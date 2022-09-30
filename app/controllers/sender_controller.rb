require 'open3'
class SenderController < ApplicationController
    def index
    end

    def gen
        @year = params[:year] 
        @field = params[:field]
        @time = params[:time]
        @day = params[:day]
        
        #Managefile.create!(name:"#{@year}_#{@field}_#{@time}_#{@day}",path:"resources/csv/#{@year}_#{@field}_#{@time}_#{@day}.csv")
        
        #p`python3 resources/scripts/keiba.py #{@year} #{@field} #{@time} #{@day}`

        KeibapyJob.perform_later(@year,@field,@time,@day,2)
        #KeibapyJob.perform_later(2022,"札幌",1,1)

        #download_file_name = "tmp/test.txt"
        #send_file download_file_name
        
        #download_file_name = "resources/csv/#{@year}_#{@field}_#{@time}_#{@day}.xlsx"

        
    end
    def s_gen
        @year = params[:year] 
        @field = params[:field]
        @time = params[:time]
        @day = params[:day]
        
        #Managefile.create!(name:"#{@year}_#{@field}_#{@time}_#{@day}",path:"resources/csv/#{@year}_#{@field}_#{@time}_#{@day}.csv")
        
        #p`python3 resources/scripts/keiba.py #{@year} #{@field} #{@time} #{@day}`

        KeibapyJob.perform_later(@year,@field,@time,@day,1)

    end

    def t_gen
        @year = params[:year] 
        @field = params[:field]
        @time = params[:time]
        @day = params[:day]
        
        #Managefile.create!(name:"#{@year}_#{@field}_#{@time}_#{@day}",path:"resources/csv/#{@year}_#{@field}_#{@time}_#{@day}.csv")
        
        #p`python3 resources/scripts/keiba.py #{@year} #{@field} #{@time} #{@day}`

        KeibapyJob.perform_later(@year,@field,@time,@day,0)
    end

end
