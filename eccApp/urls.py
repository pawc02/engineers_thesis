from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home_page'),
    path('ecdsa/', views.ecdsa_page, name='ecdsa_page'),
    path('elgamal/', views.elgamal_page, name='elgamal_page'),
    path('lenstra/', views.lenstra_page, name='lenstra_page'),

    # Użytkownik aplikacji
    path('generate_keys/', views.generate_keys_view, name='generate_keys'),
    path('users/', views.users_view, name='users'),
    path('users/<int:key_id>/', views.user_detail_view, name='user_detail'),
    path('change_parameters/<int:key_id>/', views.change_user_parameters, name='change_parameters'),
    path('delete_user/<int:key_id>/', views.delete_user_view, name='delete_user'),

    # Algorytm ElGamala
    path('elgamal/encrypt/', views.elgamal_encrypt_view, name='elgamal_encrypt'),
    path('elgamal/encrypt/<int:key_id>/', views.elgamal_encrypt_view, name='elgamal_encrypt_to_user'),
    path('elgamal/messages/', views.elgamal_messages, name='elgamal_messages'),
    path('elgamal/messages/<int:message_id>/', views.elgamal_message_detail, name='elgamal_message_detail'),
    path('elgamal/decrypt/', views.elgamal_decrypt_view, name='elgamal_decrypt'),
    path('elgamal/decrypt/<int:message_id>/', views.elgamal_decrypt_view, name='elgamal_decrypt_with_id'),
    path('elgamal/delete_message/<int:message_id>/', views.elgamal_delete_message, name='elgamal_delete_message'),

    # Algorytm ECDSA
    path('ecdsa/sign/', views.ecdsa_sign_view, name='ecdsa_sign'),
    path('ecdsa/sign/<int:key_id>/', views.ecdsa_sign_view, name='ecdsa_sign'),
    path('ecdsa/messages/', views.ecdsa_messages, name='ecdsa_messages'),
    path('ecdsa/messages/<int:message_id>/', views.ecdsa_message_detail, name='ecdsa_message_detail'),
    path('ecdsa/verify/', views.ecdsa_verify_view, name='ecdsa_verify'),
    path('ecdsa/verify/<int:message_id>/', views.ecdsa_verify_view, name='ecdsa_verify_with_id'),
    path('ecdsa/delete_message/<int:message_id>/', views.ecdsa_delete_message, name='ecdsa_delete_message'),

    # Algorytm faktoryzacji Lenstry
    path('lenstra/factorize/', views.lenstra_factorize, name='lenstra_factorize'),

    # Operacje na krzywych
    path('curve_operations/', views.curve_operations, name='curve_operations'),
    path('curve_operations/add_points/', views.add_points, name='add_points'),
    path('curve_operations/multiply_point/', views.multiply_point, name='multiply_point'),
    path('curve_operations/show_multiples_of_point/', views.show_multiples_of_point, name='show_multiples_of_point'),
    # Endpoint do pobierania wykresu
    path('curve_operations/get_plot_for_multiple/', views.get_plot_for_multiple, name='get_plot_for_multiple'),
    path('curve_operations/show_curve_graph/', views.show_curve_graph, name='show_curve_graph'),
]
