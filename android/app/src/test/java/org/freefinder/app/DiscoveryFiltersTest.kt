package org.freefinder.app
import org.junit.Assert.*
import org.junit.Test
class DiscoveryFiltersTest {
    private val offer=Offer(id="a",name="Printed poster",url="https://example.org/poster",brand="USGS",platform="USGS Store",status="pending")
    @Test fun filtersCombineBrandPlatformAndStatus(){
        assertTrue(Filters(brand="USGS",platform="USGS Store",status="pending").matches(offer))
        assertFalse(Filters(brand="Other").matches(offer))
        assertFalse(Filters(status="verified").matches(offer))
    }
    @Test fun unknownDestinationRequiresExplicitOptIn(){
        assertFalse(Filters(country="AD").matches(offer))
        assertTrue(Filters(country="AD",includeUnknown=true).matches(offer))
        assertFalse(Filters(country="AD",includeUnknown=true).matches(offer.copy(shippingAd="unavailable")))
    }
}
