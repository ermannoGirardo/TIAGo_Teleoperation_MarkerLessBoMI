
"use strict";

let DisableEmergency = require('./DisableEmergency.js')
let FinalApproachPose = require('./FinalApproachPose.js')
let RenameMap = require('./RenameMap.js')
let SetSubMapFloor = require('./SetSubMapFloor.js')
let VisualLocRecognize = require('./VisualLocRecognize.js')
let GetSubMap = require('./GetSubMap.js')
let SafetyZone = require('./SafetyZone.js')
let GetNodes = require('./GetNodes.js')
let GetMapConfiguration = require('./GetMapConfiguration.js')
let ChangeBuilding = require('./ChangeBuilding.js')
let SaveMap = require('./SaveMap.js')
let SetPOI = require('./SetPOI.js')
let Acknowledgment = require('./Acknowledgment.js')
let ListMaps = require('./ListMaps.js')
let GetPOI = require('./GetPOI.js')
let SetMapConfiguration = require('./SetMapConfiguration.js')
let ChangeMap = require('./ChangeMap.js')

module.exports = {
  DisableEmergency: DisableEmergency,
  FinalApproachPose: FinalApproachPose,
  RenameMap: RenameMap,
  SetSubMapFloor: SetSubMapFloor,
  VisualLocRecognize: VisualLocRecognize,
  GetSubMap: GetSubMap,
  SafetyZone: SafetyZone,
  GetNodes: GetNodes,
  GetMapConfiguration: GetMapConfiguration,
  ChangeBuilding: ChangeBuilding,
  SaveMap: SaveMap,
  SetPOI: SetPOI,
  Acknowledgment: Acknowledgment,
  ListMaps: ListMaps,
  GetPOI: GetPOI,
  SetMapConfiguration: SetMapConfiguration,
  ChangeMap: ChangeMap,
};
