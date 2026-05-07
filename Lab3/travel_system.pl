% travel_system.pl
% Versión adaptada: transport ∈ {plane, other}, cost ∈ {low, high}
% Diseñado para trabajar con travel_agent.pl que tiene hechos del estilo:
% transport("Amsterdam", plane).   cost("Zurich", high).
% restaurant("Amsterdam","Gartine"). cuisine("Gartine","Vegan Options").
% travel_guide("Warsaw","DK Eyewitness Poland","DK Eyewitness").

:- consult('travel_agent.pl').

print_list([]).
print_list([H|T]) :-
    write('- '), write(H), nl,
    print_list(T).

take_n(_, 0, []) :- !.
take_n([], _, []) :- !.
take_n([H|T], N, [H|R]) :-
    N1 is N - 1,
    take_n(T, N1, R).

%% ---------- BUSCAR CIUDADES (transport: plane|other|any, budget: low|high|any) ----------
suggest_city :-
    write('Which transport do you prefer? (plane/other or any)'), nl,
    read(TransportRaw),
    write('Which budget? (low/high or any)'), nl,
    read(BudgetRaw),
    normalize_transport(TransportRaw, Transport),
    normalize_budget(BudgetRaw, Budget),
    find_cities(Transport, Budget, Cities),
    ( Cities == [] ->
        write('No cities found for those constraints.'), nl
    ; write('Suggested cities:'), nl, print_list(Cities)
    ).

% Normalización: aceptar tanto plane/other atoms como 'any'
normalize_transport(any, any) :- !.
normalize_transport(Transport, Transport) :- member(Transport, [plane, other]).
normalize_transport(Other, Other) :- atom(Other), Other == any.

normalize_budget(any, any) :- !.
normalize_budget(B, B) :- member(B, [low, high]).
normalize_budget(Other, Other) :- atom(Other), Other == any.

% find_cities: recoge ciudades que cumplan transporte y presupuesto.
% Si Budget=low/high y cost(City,Cost) no existe, la ciudad no se incluye.
find_cities(Transport, Budget, CitiesUnique) :-
    findall(City,
        ( transport(City, T),
          ( Transport == any -> true ; T == Transport ),
          ( Budget == any ->
              true
          ; cost(City, Cost) -> Cost == Budget
          )
        ),
    CitiesDup),
    sort(CitiesDup, CitiesUnique).

%% ---------- SUGERIR LANDMARKS ----------

% Usa findnsols para tomar los primeros N landmarks de una ciudad
suggest_landmark :-
    write('Enter city name (e.g. "Amsterdam"): '), nl,
    read(City),
    write('How many landmarks do you want? (1-5): '), nl,
    read(Nraw),
    % normalizar N al rango 1..5
    (   integer(Nraw) ->
        ( Nraw < 1 -> N1 = 1
        ; Nraw > 5 -> N1 = 5
        ; N1 = Nraw
        )
    ;   % si el usuario no da un entero, tomar 1 por defecto
        write('Invalid number, using 1.'), nl,
        N1 = 1
    ),
    % encontrar hasta N1 landmarks
    findnsols(N1, L, landmark(City, L), Landmarks),
    ( Landmarks == [] ->
        write('No landmarks found for that city.'), nl
    ; write('Landmarks:'), nl,
      print_list(Landmarks),
      nl,
      % sugerir travel guide si existe
      ( travel_guide(City, Title, Author) ->
            write('Suggested travel guide:'), nl,
            write('  Title: '), write(Title), nl,
            write('  Author: '), write(Author), nl
      ;   write('No travel guide found for that city in the database.'), nl
      )
    ).

%% ---------- SUGERIR RESTAURANTES ----------
% ?- suggest_restaurant.
% Enter city name (e.g. "Zurich").
% Enter preferred cuisine (e.g. "Vegan Options").
% Enter maximum price range (1..3).
% Enter minimum average rating (e.g. 4.5).

% convierte entrada (atom o string) a STRING (porque travel_agent.pl usa strings)
normalize_to_string(X, S) :-
    ( string(X) -> S = X
    ; atom(X)   -> atom_string(X, S)
    ; % caso inesperado: convertir usando write_term_to_atom como fallback
      write('Warning: unexpected input type, converting to atom-string fallback.'), nl,
      term_to_atom(X, A),
      atom_string(A, S)
    ).

suggest_restaurant :-
    write('Enter city name (e.g. "Zurich"): '), nl,
    read(CityRaw),
    write('Enter preferred cuisine (e.g. "Vegan Options"): '), nl,
    read(CuisineRaw),
    write('Enter maximum price range you are willing to pay (1 = $, 2 = $$, 3 = $$$): '), nl,
    read(MaxPriceRaw),
    write('Enter minimum average rating required (e.g. 4.5): '), nl,
    read(MinRatingRaw),

    % Normalizar ciudad y cocina a strings para que coincidan con travel_agent.pl
    normalize_to_string(CityRaw, City),
    normalize_to_string(CuisineRaw, Cuisine),

    % Normalizar MaxPrice a entero en 1..3
    ( number(MaxPriceRaw) ->
        MaxPriceIntTemp is integer(MaxPriceRaw),
        ( MaxPriceIntTemp < 1 -> MaxPrice = 1
        ; MaxPriceIntTemp > 3 -> MaxPrice = 3
        ; MaxPrice = MaxPriceIntTemp
        )
    ; write('Invalid max price, using 3 (highest).'), nl, MaxPrice = 3
    ),

    % Normalizar MinRating a número; si falla, usar 0.0
    ( number(MinRatingRaw) -> MinRating = MinRatingRaw
    ; write('Invalid minimum rating, using 0.0.'), nl, MinRating = 0.0
    ),

    % Buscar coincidencias: restaurante en City (string), que ofrezca Cuisine (string),
    % con price_range <= MaxPrice y rating >= MinRating
        % Buscar coincidencias como entries
    findall(price_entry(Price, Name, Rating),
        (
            restaurant(City, Name),
            cuisine(Name, Cuisine),
            price_range(Name, Price),
            rating(Name, Rating),
            Price =< MaxPrice,
            Rating >= MinRating
        ),
    Matches),

    ( Matches == [] ->
        write('No restaurants found that match your criteria.'), nl
    ;
      % ordenar por Price asc y Rating desc
      predsort(restaurant_cmp, Matches, SortedMatches),

      write('Suggested restaurants (price | name | rating):'), nl,
      print_restaurant_entries(SortedMatches),

      findall(N, member(price_entry(_,N,_), SortedMatches), Names),
      write('Names list: '), write(Names), nl
    ).

% comparator y printer auxiliares (añádelos al final del archivo)
restaurant_cmp(Order, price_entry(P1,_,R1), price_entry(P2,_,R2)) :-
    ( P1 < P2 -> Order = '<'
    ; P1 > P2 -> Order = '>'
    ; ( R1 > R2 -> Order = '<'
      ; R1 < R2 -> Order = '>'
      ; Order = '='
      )
    ).

print_restaurant_entries([]).
print_restaurant_entries([price_entry(P,Name,R)|T]) :-
    write('- '), write(Name),
    write(' | price_range: '), write(P),
    write(' | rating: '), write(R), nl,
    print_restaurant_entries(T).
