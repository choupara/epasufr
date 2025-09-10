1 { living(plant); living(animal) } 1.
1 { animal_type(vertebrate); animal_type(invertebrate) } 1 :- living(animal).
1 { plant_type(algae); plant_type(moss); plant_type(fern); plant_type(tree) } 1 :- living(plant).
1 { invertebrate_type(sponge); invertebrate_type(worm) } 1:- animal_type(invertebrate).
1 { vertebrate_type(fish); vertebrate_type(mammal) } 1:- animal_type(vertebrate).
1 { mammal_type(herbivore); mammal_type(carnivore); mammal_type(omnivore) } 1:- vertebrate_type(mammal).
example(herbivore, cow) :- mammal_type(herbivore).
example(carnivore, lion) :- mammal_type(carnivore).
example(omnivore, human) :- mammal_type(omnivore).

#project animal_type(vertebrate).
%#project mammal_type(herbivore).
