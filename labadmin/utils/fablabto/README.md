# Changes needed to the plone app

Add these packages to the buildout.cfg:

```
diff --git a/buildout.cfg b/buildout.cfg
index febc3d3..1492858 100644
--- a/buildout.cfg
+++ b/buildout.cfg
@@ -74,6 +74,8 @@ eggs =
     z3c.jbot
     fablab.portal
     Products.PloneFormGen
+    simplejson
+    collective.jsonify
 
 ############################################
 # ZCML Slugs
```

And the follow the [https://collectivejsonify.readthedocs.io/en/latest/#how-to-install-it](instructions) to create the necessary External Methods.

You need to patch the fablab portal app with this patch:

```
diff --git a/fablab/portal/browser/member_view.pt b/fablab/portal/browser/member_view.pt
index a92c81d..37a4d34 100644
--- a/fablab/portal/browser/member_view.pt
+++ b/fablab/portal/browser/member_view.pt
@@ -10,16 +10,16 @@
 <metal:content-core fill-slot="content-core">
     <metal:content-core define-macro="content-core">
         <div class="member-portrait">
-            <img tal:replace="structure view/portrait" />
+            <img id="immagine" tal:replace="structure view/portrait" />
         </div>
         <div tal:condition="view/location">
             <label i18n:translate="">Location:</label>
-            <span tal:content="view/location" />
+            <span id="luogo" tal:content="view/location" />
         </div>
         <div tal:define="interests view/interests"
              tal:condition="interests">
             <label i18n:translate="">Interests:</label>
-            <span tal:content="interests" />
+            <span id="interessi" tal:content="interests" />
         </div>
         <div tal:condition="view/is_owner_or_manager">
             <label i18n:translate="">Credits:</label>
@@ -27,7 +27,7 @@
         </div>
         <div tal:condition="view/biography">
             <label i18n:translate="">Biography:</label>
-            <p tal:content="view/biography" />
+            <p id="biografia" tal:content="view/biography" />
         </div>
         <tal:y define="workshops view/workshops"
                condition="workshops">
```

Now you can run the script to scrape the plone app!
