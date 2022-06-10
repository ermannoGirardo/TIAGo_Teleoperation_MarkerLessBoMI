
"use strict";

let SetDatabase = require('./SetDatabase.js')
let Recognizer = require('./Recognizer.js')
let AddTexturedObject = require('./AddTexturedObject.js')
let StopEnrollment = require('./StopEnrollment.js')
let ChangeObjectRecognizerModel = require('./ChangeObjectRecognizerModel.js')
let StartEnrollment = require('./StartEnrollment.js')
let SelectTexturedObject = require('./SelectTexturedObject.js')

module.exports = {
  SetDatabase: SetDatabase,
  Recognizer: Recognizer,
  AddTexturedObject: AddTexturedObject,
  StopEnrollment: StopEnrollment,
  ChangeObjectRecognizerModel: ChangeObjectRecognizerModel,
  StartEnrollment: StartEnrollment,
  SelectTexturedObject: SelectTexturedObject,
};
