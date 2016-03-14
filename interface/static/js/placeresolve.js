/**
 * Created by tla on 10/03/16.
 */

// Global var(s)
var themap;
var currentLayer;
var currentData;

function init_map () {
     // Initialize the map if it has not been so far
    if(!themap) {
        L.mapbox.accessToken = 'pk.eyJ1IjoidGxhIiwiYSI6ImNpbHFiZG5ndDAwNG55YW0wNmZnY3g5anEifQ.KjCjqHAqQzpX6XS_VDfWlQ';
        themap = L.mapbox.map('map', 'mapbox.streets');
    }
}

function loadmap(resultdiv) {
    // Initialize the map if it has not been so far
    init_map();
    // Clear error and set the row color
    $("#error").empty();
    $("#saveresult").empty();
    $("#mappane").show();
    $(".searchresult").removeClass("selected");
    resultdiv.addClass("selected");

    // Remove the existing layer
    if(currentLayer && themap.hasLayer(currentLayer)) {
        themap.removeLayer(currentLayer)
    }
    //noinspection JSUnresolvedVariable
    var osm_id = resultdiv.data("osmdata").osm_id;
    //noinspection JSUnresolvedVariable
    var osm_type = resultdiv.data("osmdata").osm_type;
    var osm_url = "https://www.openstreetmap.org/api/0.6/" + osm_type + "/" + osm_id;
    if (osm_type != "node") {
        osm_url += "/full";
    }
    $.ajax({
        url: osm_url, dataType: "xml", success: function (xml) {
            currentData = xml;
            currentLayer = new L.OSM.DataLayer(xml).addTo(themap);
            themap.fitBounds(currentLayer.getBounds());
        }
    });
}

function geosearch () {
    // Send the AJAX query
    $("#error").empty();
    $("#saveresult").empty();
    $.getJSON('/interface/placequery', $("#geosearch").serialize(), function(resp) {
        // Hide the form and replace it with a table full of the results
        var resultbox = $("#queryresults");
        resultbox.empty();
        resultbox.show();
        if( resp.length > 0 ) {
            $.each(resp, function (i, record) {
                // Get the template as an HTML string
                var rowstr = $('#candidate').html();
                // Substitute the relevant values
                rowstr = rowstr.replace('__NAME__', record.display_name);
                rowstr = rowstr.replace('__CLASS__', record.class);
                rowstr = rowstr.replace('__TYPE__', record.type);
                var row = $(rowstr);
                resultbox.append(row);
                row.data("osmdata", record);
                row.click(function() {loadmap($(this))});
            });
        } else {
            resultbox.html('<p> No results found for this place name. Try another name?</p>');
        }
    });
}

$(document).ready( function () {
    $('#geosearch').hide();
    $('#mappane').hide();

    $(".location").click( function() {
        // Empty work boxes
        $("#error").empty();
        $("#saveresult").empty();
        $("#queryresults").hide();
        // Mark the place that is currently selected
        $(".info").removeClass("info");
        $(this).addClass("info");

        // Get the location ID and last-used query string
        var locid = $(this).children('.locid').text();
        var querystring = $(this).children('.qname').text();

        // Display the map if there is a saved result
        $.ajax({
            url: '/interface/place/' + locid, dataType: "xml", success: function (xml) {
                init_map();
                $("#mappane").show();
                currentData = xml;
                currentLayer = new L.OSM.DataLayer(xml).addTo(themap);
                themap.fitBounds(currentLayer.getBounds());
            }
        });

        // Fill in and display the form
        $("#locid").val(locid);
        $("#querystring").val(querystring);
        $("#geosearch").show();
    });

    $("#do_geosearch").click(geosearch);
    
    $("#save_place").click( function() {
        // Send the current OSM data back to the server for the selected place
        var url = '/interface/place/' + $(".info").children('.locid').text();
        var xmlbody = new XMLSerializer().serializeToString(currentData);
        $.post(url, xmlbody, function () {
            // Add the 'success' class to the appropriate left-hand row
            $('.info').addClass('success');
            $('#saveresult').html('<p>Place resolved!</p>');
        })
        
    });
}).ajaxError(function (event, jqXHR, settings, thrownError) {
    if(settings.url.match('/interface/place') && thrownError === "Not Found") {
        // Not really an error, just no result from the lookup
        $("#mappane").hide();
    } else {
        var p = $('<p>').text("Error fetching " + settings.url + ": " + thrownError);
        $("#error").append(p);
    }
});