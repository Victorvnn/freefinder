package org.freefinder.app
import org.junit.Assert.*
import org.junit.Test
class CatalogModesTest {
    private val item=Offer(id="1",name="Physical item",url="https://example.org/item",promoPrice=0.0,purchaseRequired=false,kind="promotion")
    @Test fun zeroProductsAreNotSamplesOrConditionalOtherTypes(){
        assertTrue(item.matchesCatalog("zero"))
        for(kind in listOf("sample","giveaway","cashback","loan","selection","keep_trial"))assertFalse(item.copy(kind=kind).matchesCatalog("zero"))
    }
    @Test fun unknownPriceOrPurchaseAndNonzeroPriceAreNotZeroProducts(){
        assertFalse(item.copy(promoPrice=null).matchesCatalog("zero"))
        assertFalse(item.copy(promoPrice=0.01).matchesCatalog("zero"))
        assertFalse(item.copy(purchaseRequired=true).matchesCatalog("zero"))
        assertFalse(item.copy(purchaseRequired=null).matchesCatalog("zero"))
    }
    @Test fun otherModesRemainAccessible(){
        assertTrue(item.copy(kind="sample").matchesCatalog("samples"))
        assertTrue(item.copy(kind="giveaway",promoPrice=null).matchesCatalog("draws"))
        assertTrue(item.copy(promoPrice=null).matchesCatalog("all_modes"))
    }
}
