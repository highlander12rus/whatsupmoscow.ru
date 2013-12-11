var vkPrser = (function() {
        /**
         * Текущая инициализированая карта
         * @type {google.maps.Map}
         */
        var googleMapObj;
        var markers = new Array();
        var proj;

        //////////////////////////////////////////
        /// Настройки отображения гугл карты /////
        //////////////////////////////////////////
        var divGoogleMaps = 'google_maps';
        var stylez = [
            {
                featureType: "all",
                elementType: "all",
                stylers: [
                    {
                        invert_lightness: true
                    },
                    {
                        saturation: -100
                    },
                    {
                        lightness: 13
                    }
                ]
            }
        ];

        var mapOptions = {
            zoom: 13,
            center: new google.maps.LatLng(55.755134, 37.620607), //Кординаты москвы
            disableDefaultUI: true,
            zoomControl: true,
            zoomControlOptions: {
                style: google.maps.ZoomControlStyle.SMALL,
                position: google.maps.ControlPosition.LEFT_CENTER
            },
            mapTypeControlOptions: {
                mapTypeIds: [google.maps.MapTypeId.ROADMAP, 'weloverussia']
            },
            minZoom: 9
        };
        var styledMapOptions = {
            name: "weloverussia"
        };


        //Слой для получения кордиант которые видит пользователь
        function ProjectOverlay(map) {
            this.setMap(map);
        }
        ;
        ProjectOverlay.prototype = new google.maps.OverlayView();
        ProjectOverlay.prototype.onAdd = function() {
        };
        ProjectOverlay.prototype.onRemove = function() {
        };
        ProjectOverlay.prototype.draw = function() {
        };


        //Слой для получения кордиант которые видит пользователь
        function OverlayForAnimationMarker(map, lat, lng) {
            this.latLng = new google.maps.LatLng(lat, lng);
            this.image = '/img/starlight.png';
            this.ImageSize = 17;

            this.lat = lat;
            this.lng = lng;

            this.imageInDiv = null
            /**
             * 
             * @type {google.maps.Map}
             */
            this.map_ = map;

            this.div_ = null;
            this.setMap(map);
        }
        ;

        OverlayForAnimationMarker.prototype = new google.maps.OverlayView();
        OverlayForAnimationMarker.prototype.onAdd = function() {
            this.div_ = document.createElement('div');
            this.div_.style.width = this.ImageSize + "px";
            this.div_.style.height = this.ImageSize + "px";
            this.div_.style.position = "absolute";
            this.div_.style.opacity = "0.0";
            this.div_.style.top = "0px";
            this.div_.style.left = "0px";

            //insert image
            this.imageInDiv = document.createElement('img');
            this.imageInDiv.src = this.image;
            this.imageInDiv.width = this.ImageSize;
            this.imageInDiv.height = this.ImageSize;
            this.div_.appendChild(this.imageInDiv)

            this.isStartAnimation = false;

            this.getPanes().overlayMouseTarget.appendChild(this.div_);
            var self = this;
            this.Reverser_anim = function() {
                $(this.div_).animate({
                    opacity: 0.0
                }, {
                    complete: function() {
                        //Добавляем обычный маркер т.к он быстрее работает
                        var marker = new google.maps.Marker({
                            position: new google.maps.LatLng(self.lat, self.lng),
                            map: googleMapObj,
                            'icon': 'http://whatsupmoscow.ru/img/geo_7.png'
                        });
                        markers.push(marker);
                        self.RemoveDiv();
                    },
                    duration: 500
                });
            }

            $(this.div_).animate({
                opacity: 1.0
            }, {
                complete: function() {
                    self.Reverser_anim()
                },
                duration: 500
            });


        };
        OverlayForAnimationMarker.prototype.RemoveDiv = function() {
            this.getPanes().overlayMouseTarget.removeChild(this.div_);
            this.setMap(null);
        }

        OverlayForAnimationMarker.prototype.onRemove = function() {
            this.div_.removeChild(this.imageInDiv)
            this.div_ = null
            this.setMap(null);
        };
        OverlayForAnimationMarker.prototype.draw = function() {
            var overlayProjection = this.getProjection();
            var cordinate = overlayProjection.fromLatLngToDivPixel(this.latLng);
            var centerImage = this.ImageSize / 2;
            this.div_.style.left = (cordinate.x - centerImage) + "px";
            this.div_.style.top = (cordinate.y - centerImage) + "px";
        };


        function InitGoogleMaps() {
            googleMapObj = new google.maps.Map(document.getElementById(divGoogleMaps),
                    mapOptions);

            var styledMapType = new google.maps.StyledMapType(stylez, styledMapOptions);
            googleMapObj.mapTypes.set('weloverussia', styledMapType);
            googleMapObj.setMapTypeId('weloverussia');

            proj = new ProjectOverlay(googleMapObj);

            google.maps.event.addListener(proj, 'projection_changed', function() {
                projOverlay = proj.getProjection();
            });

        }
        ;

        $(function() {
            InitGoogleMaps();
        });
        return {
            setMarkers: function(lat, lng, img_marker) {
                var latLng = new google.maps.LatLng(lat, lng);
                var marker = new google.maps.Marker({
                    position: latLng,
                    map: googleMapObj,
                   'icon': img_marker
                });
                markers.push(marker);
            },
            setAnimMarker: function(lat, lng) {
                new OverlayForAnimationMarker(googleMapObj, lat, lng);
            }
        };
    })();

    

    
    $(function() {
        $.get('/map/get/', function(data) {
            for (var i in data.collection) {
                vkPrser.setMarkers(data.collection[i].loc[1],
                        data.collection[i].loc[0],
                        'http://whatsupmoscow.ru/img/geo_7.png');
            }
        }, 'json')
                .error(function() {
            alert('Ошибка получения информации о метках, пожалуйста, попробуйте еще раз.')
        });

        if ("WebSocket" in window) {
            //use websocket for online update
            var socket = new WebSocket("ws://whatsupmoscow.ru:8080/ws");
            socket.onmessage = function(event) {
                console.log("message was send");
                var arrayLatlng = $.parseJSON(event.data);
                for (var i in arrayLatlng) {
                    console.log(arrayLatlng[i])
                    vkPrser.setAnimMarker(arrayLatlng[i][1], arrayLatlng[i][0]);
                }
            };
        }
    })