package org.freefinder.app
import org.junit.Assert.*
import org.junit.Test

class FiltersTest {
    private fun offer()=Offer(id="test",name="Synthetic fixture",url="https://example.org/item",category="office")
    @Test fun unknownShippingIsNotFreeOrConfirmed(){
        val o=offer()
        assertFalse(Filters(country="AD").matches(o))
        assertFalse(Filters(country="ES").matches(o))
        assertFalse(Filters(maxShipping=0.0).matches(o))
        assertTrue(Filters().matches(o))
    }
    @Test fun purchaseConditionsExcluded(){assertFalse(Filters().matches(offer().copy(purchaseRequired=true)))}
    @Test fun keepableMustBeExplicit(){assertFalse(Filters(keepOnly=true).matches(offer()));assertTrue(Filters(keepOnly=true).matches(offer().copy(keepable=true)))}
    @Test fun categoryAndTypeCombine(){val f=Filters(category="office",kind="sample");assertFalse(f.matches(offer()));assertTrue(f.matches(offer().copy(kind="sample")))}
    @Test fun bothCountriesRequireBoth(){assertFalse(Filters(country="both").matches(offer().copy(shippingEs="confirmed")));assertTrue(Filters(country="both").matches(offer().copy(shippingEs="confirmed",shippingAd="confirmed")))}
    @Test fun bothCountriesMaximumShippingChecksBoth(){
        val o=offer().copy(shippingEs="confirmed",shippingAd="confirmed",shippingCostEs=0.0,shippingCostAd=25.0)
        assertFalse(Filters(country="both",maxShipping=5.0).matches(o))
    }
}
