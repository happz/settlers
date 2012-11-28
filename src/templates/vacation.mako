<%!
  import time
  import lib.trumpet
%>

<%namespace file="hlib_ui.mako" import="*" />

<%inherit file="page.mako" />

<form action="/vacation/kill" method="post">
  <fieldset>
    <legend>${_('Vacation termination')}</legend>
    <div style="text-align: justify">
      ${lib.trumpet.VacationTermination().text}
      <br />
      <br />
      <span style="font-weight: bold">
        ${_('Vacation running:')}
        ${_('From')}
        ${time.strftime(user.date_format, time.localtime(user.last_vacation.start))}
        ${_('to')}
        ${time.strftime(user.date_format, time.localtime(user.last_vacation.start + user.last_vacation.length))}
        (${int(user.last_vacation.length / 86400)} days, ${int((user.last_vacation.length % 86400) / 3600)} hours)
      </span>
    </div>
    <a href="/vacation/kill">${_('Yes, I want to cancel my vacation')}</a>
  </fieldset>
</form>
