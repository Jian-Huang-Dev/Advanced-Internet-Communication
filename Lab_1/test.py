class Pet(object):
    name = None
    type = None

Pets = []
for i in range(0, 10):
    print i
    nextpet = Pet()
    Pets.append(nextpet)

Pets[1].name = 'Dude'
Pets[1].type = 'Dog'

print 'length', len(Pets)
