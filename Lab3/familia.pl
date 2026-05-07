% family.pl
% Hechos: male/1, female/1, parent/2
% Reglas: mother, father, sibling, brother, sister,
%         grandparents, aunt, uncle, nephew, niece, cousin

% -------------------------------
% SEX FACTS
% -------------------------------

female(naia).       % hermana
female(ana).        % madre
female(marijose).   % abuela materna
female(josefa).     % abuela paterna
female(iratxe).     % tia paterna o materna?
female(cristina).   % prima
female(berta).      % prima

male(asier).        % yo
male(guillermo).    % padre
male(julio).        % abuelo materno
male(gonzalo).      % abuelo paterno
male(txetxu).       % tío
male(miguel).       % tío

% -------------------------------
% PARENT FACTS
% Solo usamos personas que aparecen arriba
% -------------------------------

% Mis padres
parent(guillermo, asier).
parent(ana,      asier).

parent(guillermo, naia).
parent(ana,      naia).

% Abuelos maternos → madre = ana
parent(marijose, ana).
parent(julio,    ana).

% Abuelos paternos → padre = guillermo
parent(josefa,  guillermo).
parent(gonzalo, guillermo).

parent(josefa, txetxu).
parent(gonzalo, txetxu).

% Tíos maternos o paternos (según quieras)
% Aquí pongo que son hermanos de mi madre
parent(marijose, iratxe).
parent(julio,    iratxe).

% Primos (hijos de mis tíos)
% Ojo: solo podemos crear primos si existen padres válidos
parent(iratxe, cristina).
parent(miguel, berta).

% -------------------------------
% REGLAS
% -------------------------------

mother(M,C) :- female(M), parent(M,C).

father(F,C) :- male(F), parent(F,C).

% Hermanos: comparten un padre o una madre
sibling(X,Y) :-
    parent(P,X),
    parent(P,Y),
    X \= Y.

brother(X,Y) :- male(X), sibling(X,Y).
sister(X,Y)  :- female(X), sibling(X,Y).

% Abuelos
grandmother(G,C) :- female(G), parent(G,P), parent(P,C).
grandfather(G,C) :- male(G), parent(G,P), parent(P,C).

% Tíos
aunt(A,C) :-
    female(A),
    parent(P,C),
    sibling(A,P).

uncle(U,C) :-
    male(U),
    parent(P,C),
    sibling(U,P).

% Sobrinos
nephew(N,A) :-
    male(N),
    parent(P,N),
    sibling(P,A).

niece(N,A) :-
    female(N),
    parent(P,N),
    sibling(P,A).

% Primos
cousin(X,Y) :-
    parent(Px,X),
    parent(Py,Y),
    sibling(Px,Py),
    X \= Y.
