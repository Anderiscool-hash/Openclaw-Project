(function (factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as anonymous module.
        define('datepicker.es-ES', ['jquery'], factory);
    } else if (typeof exports === 'object') {
        // Node / CommonJS
        factory(require('jquery'));
    } else {
        // Browser globals.
        factory(jQuery);
    }
})(function ($) {

    'use strict';

    $.fn.datepicker.languages['es-ES'] = {
        format: 'dd-mm-yyyy',
        days: ['Domingo','Lunes','Martes','Miércoles','Jueves','Viernes','Sábado'],
        daysShort: ['Dom','Lun','Mar','Mie','Jue','Vie','Sab'],
        daysMin: ['Do','Lu','Ma','Mi','Ju','Vi','Sa'],
        weekStart: 0,
        months: ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'],
        monthsShort: ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic']
    };
});
function App(options) {
    var self = this;
    var _settings = $.extend({}, options);
    this.data = ko.observableArray();

    this.getTodayDate = function() {
        var d = new Date();

        var month = d.getMonth()+1;
        var day = d.getDate();

        return (day<10 ? '0' : '') + day + '-' + (month<10 ? '0' : '')+ month + '-' + d.getFullYear();
    };

    this.selectedDate = ko.observable(_settings.today);

    this.selectedDate.subscribe(function(value){
        var newLocation = self.updateURLParameter(window.location.href, 'date', value);
        window.location.href = newLocation;
        //self.resetAutoRefresh();
        //self.getAllSessions();
    });

    this.updateURLParameter = function (url, param, paramVal){
        var newAdditionalURL = "";
        var tempArray = url.split("?");
        var baseURL = tempArray[0];
        var additionalURL = tempArray[1];
        var temp = "";
        if (additionalURL) {
            tempArray = additionalURL.split("&");
            for (var i=0; i<tempArray.length; i++){
                if(tempArray[i].split('=')[0] != param){
                    newAdditionalURL += temp + tempArray[i];
                    temp = "&";
                }
            }
        }

        var rows_txt = temp + "" + param + "=" + paramVal;
        return baseURL + "?" + newAdditionalURL + rows_txt;
    };

    this.getAllSessions = function(){
        var _data = {
            cb: Math.round(new Date().getTime() / 1000),
            date: self.selectedDate()
        };

        if (_settings.company_id) {
            _data.company_id = _settings.company_id;
        }
        if (_settings.game_id) {
            _data.game_id = _settings.game_id;
        }

        $.ajax({
            url: _settings.url,
            type: "GET",
            data: _data,
            success: function(response){
                var str = "";
                response = response.toString();
                for (var o = 0; o < response.length; o++) {
                    var a = response.charCodeAt(o);
                    var b = a ^ _settings.key;
                    str = str + String.fromCharCode(b);
                }
                try{
                    response = JSON.parse(str);
                } catch (err) {
                    window.location.reload(true);
                    return true;
                }
                var data = [ [] ];
                var gameIterator = 0;
                for(var i = 0; i< response.length; i++) {
                    data[data.length - 1].push(new LotteryCompany(response[i]));
                    if(gameIterator%5 == 3) {
                        gameIterator--;
                    }
                    for(var key in response[i].lotterySiteGames) {
                        if(gameIterator%5 == 3 && data.length <= 2) {
                            data.push([]);
                        }
                        if(response[i].lotterySiteGames[key].lotteryGame.lotterySession) {
                            data[data.length - 1].push(new LotteryGame(response[i].lotterySiteGames[key]));
                        }

                        gameIterator++;
                    }
                }
                self.data(data);
            }
        });
    };


    var timer = false;
    this.resetAutoRefresh = function(){
        if(timer !== false) {
            clearInterval(timer);
        }
        timer = setInterval(self.getAllSessions, 6000*1000);
    };

    this.resetAutoRefresh();

    this.getBallCss = function(score) {
        var firstChar = score.charAt(0);

        switch (firstChar) {
            case '+':
                return 'bonus';
            case '!':
                return 'special1';
            case '=':
                return 'special2';
            case '?':
                return 'special3';
            default:
                return '';
        }

        return '';
    }
}

function LotteryCompany(data) {
    this.permalink = data.permalink;
    this.title = data.title;
}

function LotteryGame(data) {
    var self = this;
    this.permalink = data.permalink;
    this.title = data.title;
    this.skip = data.lotteryGame.skip;
    this.delay = data.lotteryGame.delay;
    this.logoUrl = data.lotteryGame.logoUrl;
    this.result_view_mode = data.lotteryGame.result_view_mode;

    this.shitFound = false;
    this.checkForSpecialShit = function(){
        if (self.score.join(' ').indexOf('?')!=-1) {

            console.log('gyot moment');
            for(var i = 0; i < self.score.length; i++) {
                self.score[i] = self.score[i].split(' ');
            }
            self.shitFound = true;
            return true;
        }

        return false;
    };

    if(data.lotteryGame.lotterySession) {
        if(data.lotteryGame.lotterySession.constructor !== Array) {
            this.date = data.lotteryGame.lotterySession.date;
            this.score = data.lotteryGame.lotterySession.score;
            this.today = data.lotteryGame.lotterySession.today;
            this.reference = data.lotteryGame.lotterySession.reference;
            this.money = data.lotteryGame.lotterySession.money;
        } else {
            this.scores = [];
            for(var i = 0; i < data.lotteryGame.lotterySession.length; i++) {
                this.scores[i] = {};
                this.scores[i].date = data.lotteryGame.lotterySession[i].date;
                this.scores[i].score = data.lotteryGame.lotterySession[i].score;
                this.scores[i].today = data.lotteryGame.lotterySession[i].today;
                this.scores[i].reference = data.lotteryGame.lotterySession[i].reference;
                this.scores[i].money = data.lotteryGame.lotterySession[i].money;
            }
        }
    }
}

