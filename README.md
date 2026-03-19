#Systeme de Surveillance Video Intelligent et de presence

#installation opencv 
#pip install opencv-contrib-python  
#pip install opencv-python mediapipe
#pip install opencv-python mtcnn keras-facenet 


#Frontend:
# **environnement de devellopement**
```
    pip install PyQt6
#Backend:
    -recquis : Sqlalchemy ,pydantic ,fastapi , python, postgresql , postman
        .commande : #pip install fastapi
                    #pip install sqlalchemy
                    #pip install psycopg2-binary
                    #pip install pydantic
    -optionnel: pgadmin
    -lancer backend : uvicorn main:app --reload
                    ny base de donnée dia créer automatiquement rehefa lancé io. Postgresql necessaire.
    Version 0.1 : Ajout eleve fonctionnel , Appelle eleve par id fonctionnel , Appelle List eleve foncionnelle
    pour frontend : route fonctionnelle  "route_eleve".
    Version 0.2 : route cours , eleve , presence fonctionnel . cd 
                -requete possible : * Ajout eleve fonctionnel ,
                                    * Appelle eleve par id fonctionnel , 
                                    * Appelle List eleve,
                                    * Creer cours
                                    * get list cours
                                    * creer presence
                                    * afficher list presence specifique d'un eleve(date/heure/status)
                                    * afficher derniere presence d'un eleve (date/heure/status)
    Version 0.3 : route ajouter et fonctionnel :
                            -route examen:
                                    .ajoute examen
                                    .afficher examen par cours
                                    
                            -route surveillance:
                                    .Creer une surveillance
                                    .Voir surveillance sur un eleve precis (id)
                            -route camera:
                                    .Creer une capture
                                    .stocker un ficher(non fonctionnel):string


#Posture detectable

 Poignets proches des épaules : Les poignets sont détectés trop proches des épaules, ce qui peut indiquer une posture suspecte.

Inclinaison excessive du torse : Le torse est incliné de manière excessive, détecté par la proximité des épaules et des hanches.

Croisement des bras : Les poignets sont détectés proches l'un de l'autre, ce qui peut indiquer un croisement des bras 
