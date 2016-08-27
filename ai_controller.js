


(function() {
  'use strict';

  function AIController() {

    // singleton
    if (this.instance_)
      return this.instance_;

    this.runner = undefined;
    this.websocket = undefined;

    this.websocket

      return this;
  }

  window['AIController'] = AIController;

  AIController.prototype = {

    init: function(runner, websocket_url) {
      this.runner = runner;
      this.websocket = new WebSocket(websocket_url);
      this.initWebSocket();

      this.last_data = {};

      this.infectRunner();
    },

    initWebSocket: function() {
      this.websocket.onopen = function() {
        console.log("[WebSocket] connection OK");
        this.sendData('speed', 6);
        this.sendData('obs_dist', 600);
        this.sendData('obs_size', 20);
        this.sendData('passed', 0);
        this.sendData('score', 0);
        this.sendData('crashed', false);
      }.bind(this)

      this.websocket.onerror = function(event) {
        console.log("[WebSocket] Error: ", event.data);
        alert("WebSocket error, AI communication closed");
      }.bind(this)

      this.websocket.onmessage = function(event) {
        raw_msg = event.data;

        console.log("[WebSocket] Receive message from AI :", raw_msg);
        msg = JSON.parse(raw_msg)
          switch (msg.type) {
            case 'action':
              doAction(msg.content);
              break;

            default:
              console.log("[WebSocket] Bad message", raw_msg);
              break;
          }
      }
    },

    doAction: function(action_type) {
      switch (action_type) {
        case 'jump':
          this.actionTRexJump();
          break;
        case 'stop':
          this.actionStop();
          break;
      }
    },

    sendData: function(key, value) {
      this.sendMsg({
        type: 'data',
        content: {
          key: key,
          value: value,
        },
      });
      this.last_data[key] = value;
    },

    getData: function(key) {
      return this.last_data[key];
    },

    sendMsg: function(msg) {
      if (this.runner === undefined
          || this.websocket === undefined
          || this.websocket.readyState !== this.websocket.OPEN) {
        //console.log("Error: Trying to send data when AIController not initialized..");
        return;
      }
      this.websocket.send(JSON.stringify(msg));
    },

    actionTRexJump: function() {
      var event = new Event(keydown ? 'keydown' : 'keyup');
      event.keyCode = 32;
      event.which = event.keyCode;
      event.altKey = false;
      event.ctrlKey = true;
      event.shiftKey = false;
      event.metaKey = false;
      this.runner.onKeyDown(event);
      this.runner.onKeyUp(event);
    },

    actionStop: function() {
      this.runner.stop();
    },

    infectRunner: function() {
      if (this.runner.infected_)
        return;
      this.runner.infected_ = true;
      var ai = this;
      var runner = this.runner;


      // Runner
      runner.update = function() {
        ai.sendData('speed', this.currentSpeed);
        Runner.prototype.update.call(runner);
      }

      runner.gameOver = function() {
        ai.sendData('crashed', true);
        Runner.prototype.gameOver.call(runner);
      }

      runner.restart = function() {
        Runner.prototype.restart.call(runner);
        ai.sendData('crashed', false);
      }

      runner.reset = function() {
        Runner.prototype.reset.call(runner);
        ai.sendData('obs_dist', 600);
        ai.sendData('obs_size', 20);
      }

      // DistanceMeter
      var dm = runner.distanceMeter;
      dm.update = function(deltaTime, distance) {
        dm.__proto__.update.call(dm, deltaTime, distance);
        var actual_distance = this.getActualDistance(distance);
        ai.sendData('score', actual_distance);
      }

      dm.reset = function() {
        dm.__proto__.update.call(dm);
        ai.sendData('passed', 0);
      }

      // Horizon
      var horiz = runner.horizon;
      horiz.updateObstacles = function(deltaTime, currentSpeed) {
        var nb_obstacles = this.obstacles.length;

        // Infos sur l'Obstacle le plus proche
        if (nb_obstacles > 0) {
          ai.sendData('obs_dist', this.obstacles[0].xPos);
          ai.sendData('obs_size', this.obstacles[0].width);
        } else {
          ai.sendData('obs_dist', 600);
          ai.sendData('obs_size', 20);
        }

        var first_obs = undefined;
        if (nb_obstacles > 0)
          first_obs = this.obstacles[0];

        horiz.__proto__.updateObstacles.call(horiz, deltaTime, currentSpeed);

        // si yavait des obs et qu'il y en a plus
        // ou si le premier obstacle n'est plus le meme
        //if ((nb_obstacles > 0 && this.obstacles.length == 0)
        //    || (first_obs !== this.obstacles[0])) 
        if (first_obs && first_obs.remove)
        {
          console.log("first_obs passed !!!!", first_obs);
          ai.sendData('passed', ai.getData('passed') + 1);
        }
      }

    } //!infectRunner

  }
})();

new AIController().init(Runner(), "ws://localhost:4242");

//

// vim:set et sw=2: