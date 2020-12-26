be = getbbsengine();
function checkcurrentmemberid()
{
    oldcurrentmemberid = be.currentmemberid;
    be.getcurrentmemberid()
        .done(function (r) {
            be.logentry("checkcurrentmemberid.done() r="+JSON.stringify(r));
            if (oldcurrentmemberid != r.currentmemberid)
            {
                be.logentry("checkcurrentmemberid.100: forcing page reload");
                be.currentmemberid = r.currentmemberid;
                window.location.reload();
                return;
            }
        })
        .fail(function (r) {
            be.logentry("checkcurrentmemberid.110: getcurrentmemberid failed "+JSON.stringify(r));
            return;
        });
    return;
}

be.addinterval(5000, "checkcurrentmemberid", checkcurrentmemberid);
