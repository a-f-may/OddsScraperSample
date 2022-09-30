Rails.application.routes.draw do
  # For details on the DSL available within this file, see http://guides.rubyonrails.org/routing.html
  root to: "sender#index"
  post "generate", to:"sender#gen"
  post "generate_t", to:"sender#t_gen"
  post "generate_s", to:"sender#s_gen"


  require 'sidekiq/web'
  mount Sidekiq::Web, at: '/sidekiq'
  
end
