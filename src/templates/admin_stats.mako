<%!
  PLUGINS = ['Accordion', 'Sound']
%>

<%

import sys
import hruntime
import hlib.size

%>

<%inherit file="page.mako" />

<%namespace file="hlib_widgets.mako"  import="*"/>

<div id="accordion">

  <fieldset>
    <legend class="accordion_toggle">${_('Cache classes')}</legend>
    <table class="accordion_content">
      <tr>
        <td>${len(hruntime.cache._classes)} classes</td>
      </tr>
      % for class_name in hruntime.cache._classes.iterkeys():
        <tr>
          <td>${class_name}</td>
        </tr>
      % endfor
    </table>
  </fieldset>

  <fieldset>
    <legend class="accordion_toggle">${_('Cache items')}</legend>
    <table  class="accordion_content">
      % for class_name, objects in hruntime.cache._objects.iteritems():
        % for object_id in objects.iterkeys():
          <tr>
            <td>${class_name}.${object_id}</td>
            <td>${hlib.size.asizeof(objects[object_id])}</td>
          </tr>
        % endfor
      % endfor
    </table>
  </fieldset>

</div>
