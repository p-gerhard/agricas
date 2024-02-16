# Agricas

Web scraper for the URL http://www.agricas.fr/menu-au-ria. It parses menus, prices and side dishes for the available days.

## Install and Run

1. Have `python >= 3.6` and `pip` installed.
2. `pip install git+https://github.com/p-gerhard/agricas` -- Install dependencies
3. `agricas -d DAYS` -- Run the script. Use the optionnal arugment `-d DAYS` with `DAYS >= 1` to choose the number days displayed. 
Use `-h` for more informations.

## Output example:

```bash
agricas -d 2
+----------------------------------------------------------------------------------------------------+
 Lun. 19 Février 2024
  - Pavé De Bœuf, Sauce Au 2 Moutardes                                                          4,20 €
  - Potimarron Rôti Au 4 Épices, Semoule Raisin Curcuma, Yaourt Harissa/Cacahuètes              3,33 €
  - Boudin Antillais Jus À L'Ananas                                                             3,33 €
  - Omelette Au Fromage                                                                         2,40 €
 Accompagnements:
  - Raves Rôtis
  - Haricots Verts
  - Fry And Dip
  - Céleris
+----------------------------------------------------------------------------------------------------+
 Mar. 20 Février 2024
  - Poulet Rôti Lr, Ail Confit Et Son Jus                                                       5,41 €
  - Gnocchis À La Betterave, Crémeux Wakamé, Grenade, Pickles D'Oignons                         2,40 €
  - Marée Fraîche, Sauce Curry Et Lait De Coco                                                  5,13 €
  - Pizza Chèvre Miel Ou Pizza Reine                                                            4,05 € ou 3,48 €
 Accompagnements:
  - Petits Pois
  - Endives Braisées Au Jus De Viande
  - Pommes De Terre Grenaille
+----------------------------------------------------------------------------------------------------+
 Mer. 21 Février 2024
  - Coquillettes Au Jambon Fumé Copeaux De Comté                                                2,40 €
  - Filet De Cabillaud Sauce Curry Et Lait De Coco                                              5,41 €
  - Escalope De Dinde Vallée D'Auge                                                             4,06 €
  - Risotto Vert Au Pesto De Roquette, Brebis, Cajou Au Curry                                   4,17 €
 Accompagnements:
  - Carottes Vapeur
  - Coquillettes Au Beurre
  - Julienne De Poireaux Sautés
+----------------------------------------------------------------------------------------------------+
```
