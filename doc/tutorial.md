# Tutorial 

In this tutorial we go through the minimal example to use staruml2json converter. All concepts of the software get explained here.

## Preparation
Get yourself an installation of [Staruml](http://staruml.io/), which can be evaluated for free. Staruml is available for Windows and Linux. We presume V3 in this tutorial. <br>
Make yourself familiar with the syntax of this tool (described on [mainpage](https://github.com/TUMFTM/Staruml2json)).
Start the Staruml editor and start a new class diagram.

### Prepare the environment for the tool
We advise to use a python virtual environment for the tool. Benefit is that you do not need to mess with the global python interpreter and its packages. 
* Install virtualenv. This might need to be done as root. `$ sudo pip install virtualenv`
* Create a new virtual environment in the folder *env* using a python3 interpreter `virtualenv env -p python3`
* Activate the environment `source env/bin/activate`
* Go to this tool's folder `cd path/to/the/tool/Staruml2json`
* Install the requirements of this tool `pip install -r requirements.txt`
You are good to go!

## Modelling
### Classes and setting up the meta model
We start modelling by adding classes to the class-diagram. Now we want to start to build up a meta model of a car.
* Add the class *simplecar* to the diagram. This is our most top level class.
* Add the class *Chassis* to the diagram.
* Add a *Composition* from *Chassis* to *simplecar*. The black rhomb is on the *simplecars* side. Additionall we add multiplications of 1 to the ends of the *Composition*. Each simplecar has exactly one Chassis.
* Add the class *Drivercabin* to the diagram.
* Add an attribute *n_seats* and let its default value be *4*.
* Add a *Composition* between *Chassis* and *Drivercabin* as described above.

<br/>
From now on, all concepts which one need to know are clear. Continue the model process, until you get the following structure. Repeat the whole process create a meta model of a trailer. 
![simple_car_meta_model](doc/simple_car_meta_model.png) ![trailer](doc/trailer_meta_model.png)

### Objects and setting up a model
Now that we have the meta model of our simplecar defined, we can turn it into a model, or a concrete instance of the defined classes. At first, we can create a new *Model* Container into our project. Into that container, we can create a new *ObjectDiagram*.

* Add an object to the new object diagram and name it  *Mycar*. As a *classifier*, we choose the class *simplecar* we defined earlier. Now we already have an "living" instance of the simplecar.
* Add a *Slot* to the object. The *definingFeature* is set to *color*, a attribute of the class *simplecar*. This links the slot with the attribute. Additionally we can add a value, e.g. value=blue.

No we decide, that our intsance of the car should get a trailer. And as we meta-modeled a trailer in advance, we can add add the trailer like so to the simplecar:
* Add a new object to the object diagram. Name it Mytrailer and set its *classifier* to the class *Trailer*.
* Add a *Link* between Mytrailer and Mycar. To make it a structural connection i.e. add the trailer's meta model to the car's, we add the keyword *structural* into the *stereotype*-field.

We now want to specify a bit more our simplecar. For example, we want to set the *max_torque* our drivetrain-class can deliver:
* Add a new object to the object diagram. Name *DT* and set its *calssifier* to the class *ElectricDrivetrain*
* Add a slot and point its *definingFeature* to the max_torque attribute. Set a value, e.g. value=100

To integrate this specific drivetrain into the simplecar, we make use of another *Link*. but this time, ElectricCrivetrain is already part of the meta-model, since we connected it in the meta model. We can use the keyword *defining* in the *stereotype*-field.
* Add a *Link* between Mycar and and DT. Set the keyword *defining* in the *stereotype*-field.

Using the *defining*-keyword advises the converter to rather replace the specified object with the one given by the meta model than adding it to the model. To add the object use the *structural*-keyword.

## Step 2: Convert to json
Now that we modeled our simplecar including trailer, we want to convert the model into a json-description.
* Start from the root folder of the tool with the new environment activated like described above.
* Convert the model `$ python src/main.py -m /example_model/simplecar.mdj -s Mycar -o my_simplecar.txt`
The output from the tool should look like so:
![output](doc/output.png)

## Step 3: Inspect result
`my_simplecar.txt` should show the following content:

`{
  "Mycar": {
    "color": {
      "type": null,
      "value": "blue"
    },
    "Chassis": {
      "Tyre": [
        {},
        {},
        {},
        {}
      ],
      "Damper": {},
      "ElectricDrivetrain": {
        "max_torque": {
          "type": null,
          "is_derrived": true,
          "value": "100"
        },
        "max_speed": {
          "type": null,
          "is_derrived": true,
          "value": "300"
        },
        "inheriting_from": "Drivetrain",
        "ElectricEngine": {},
        "Battery": {
          "voltage": {
            "type": null,
            "value": null
          },
          "SOC": {
            "type": null,
            "value": null
          }
        }
      }
    },
    "inheriting_from": "simplecar",
    "classifier": "simplecar",
    "Mytrailer": {
      "n_axes": {
        "type": null,
        "value": null
      },
      "max_load": {
        "type": null,
        "value": null
      },
      "length": {
        "type": null,
        "value": null
      },
      "n_tyres": {
        "type": null,
        "value": "4"
      },
      "Tyre": {},
      "inheriting_from": "Trailer",
      "classifier": "Trailer"
    }
  }
}`