class KeibapyJob < ApplicationJob
  queue_as :default

  def perform(y,f,d,s,w)
    # Do something later
    p`python3 resources/scripts/keiba.py #{y} #{f} #{d} #{s} #{w}`
    #p "end"
  end
end
